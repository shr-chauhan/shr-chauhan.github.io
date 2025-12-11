import type { APIRoute } from 'astro';
import OpenAI from 'openai';
import { readFileSync } from 'fs';
import { join } from 'path';

// DOCX parsing using mammoth
let mammoth: any = null;

async function loadDocxParser() {
  if (mammoth) return mammoth;
  
  try {
    const mammothModule = await import('mammoth');
    mammoth = mammothModule.default || mammothModule;
    
    if (mammoth && typeof mammoth.extractRawText === 'function') {
      console.log('✅ mammoth loaded successfully');
      return mammoth;
    } else {
      throw new Error('mammoth is not loaded correctly');
    }
  } catch (error: any) {
    console.error('❌ Failed to load mammoth:', error.message);
    console.log('💡 Tip: Run "npm install mammoth" if not installed');
    return null;
  }
}

// This API route only works in development (hybrid mode)
export const prerender = false;

// Check API key early
if (!import.meta.env.OPENAI_API_KEY) {
  console.warn('⚠️ WARNING: OPENAI_API_KEY not set in environment variables');
}

// Create OpenAI client with shorter timeout
const openai = new OpenAI({
  apiKey: import.meta.env.OPENAI_API_KEY,
  timeout: 30000, // 30 second timeout per request
  maxRetries: 0, // No retries to avoid compounding delays
});

// Load profile summary from file
let PROFILE_SUMMARY = '';

try {
  const summaryPath = join(process.cwd(), 'me', 'summary.txt');
  PROFILE_SUMMARY = readFileSync(summaryPath, 'utf-8').trim();
  console.log('✅ Loaded profile summary');
} catch (error) {
  PROFILE_SUMMARY = `Shrey Chauhan is a Senior Engineering Manager at Quantum, where he leads the Unified Surveillance Platform (USP) engineering team.`;
  console.log('⚠️ Using default profile summary');
}

// Cache for resume data
let RESUME_CACHE: string | null = null;

async function loadResume(): Promise<string> {
  if (RESUME_CACHE !== null) {
    return RESUME_CACHE;
  }

  // Try environment variable first
  if (import.meta.env.RESUME_TEXT) {
    RESUME_CACHE = import.meta.env.RESUME_TEXT;
    console.log('✅ Loaded resume from environment variable');
    return RESUME_CACHE || '';
  }

  // Try to read from me/shreyresume.docx
  try {
    const docxPath = join(process.cwd(), 'me', 'shreyresume.docx');
    const docxBuffer = readFileSync(docxPath);
    
    const mammothParser = await loadDocxParser();
    if (!mammothParser || typeof mammothParser.extractRawText !== 'function') {
      throw new Error('mammoth parser not available');
    }
    
    const result = await mammothParser.extractRawText({ buffer: docxBuffer });
    RESUME_CACHE = result.value.trim();
    console.log(`✅ Resume loaded (${RESUME_CACHE?.length || 0} chars)`);
    return RESUME_CACHE || '';
  } catch (error: any) {
    console.error('⚠️ Could not load resume:', error.message);
    RESUME_CACHE = '';
    return '';
  }
}

// Pre-load resume at startup
loadResume().catch(err => {
  console.error('Failed to pre-load resume:', err);
});

// Function definitions - SIMPLIFIED (removed tools to test if they're causing timeout)
const tools = []; // Temporarily empty to test

// Helper functions
function recordUserDetails(email: string, name: string = "Name not provided", notes: string = "not provided") {
  console.log(`📝 Recording ${name} with email ${email}`);
  return { recorded: "ok" };
}

function recordUnknownQuestion(question: string) {
  console.log(`❓ Recording unknown question: ${question}`);
  return { recorded: "ok" };
}

async function getSystemPrompt(): Promise<string> {
  const resume = await loadResume();
  
  const systemPrompt = `You are acting as Shrey Chauhan. You are answering questions on Shrey Chauhan's website, particularly questions related to Shrey Chauhan's career, background, skills and experience. Your responsibility is to represent Shrey Chauhan for interactions on the website as faithfully as possible. You are given a summary of Shrey Chauhan's background and resume which you can use to answer questions. Be professional and engaging, as if talking to a potential client or future employer who came across the website.`;

  return `${systemPrompt}\n\n## Summary:\n${PROFILE_SUMMARY}\n\n## Resume:\n${resume}\n\nWith this context, please chat with the user, always staying in character as Shrey Chauhan.`;
}

export const POST: APIRoute = async ({ request }) => {
  const startTime = Date.now();
  
  try {
    const apiKey = import.meta.env.OPENAI_API_KEY;
    if (!apiKey) {
      return new Response(JSON.stringify({ 
        error: 'OpenAI API key not configured' 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const body = await request.json();
    const { message, history } = body;
    
    if (!message) {
      return new Response(JSON.stringify({ error: 'Message is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const systemPromptContent = await getSystemPrompt();
    
    // Log the prompt length to see if it's too large
    console.log(`📊 System prompt: ${systemPromptContent.length} chars`);
    console.log(`📊 History: ${history?.length || 0} messages`);
    
    const messages: any[] = [
      { role: 'system', content: systemPromptContent },
      ...(history || []),
      { role: 'user', content: message }
    ];
    
    // Calculate approximate token count (rough estimate: 4 chars = 1 token)
    const estimatedTokens = JSON.stringify(messages).length / 4;
    console.log(`📊 Estimated tokens: ~${Math.round(estimatedTokens)}`);
    
    console.log(`💬 Request: "${message.substring(0, 40)}..."`);
    console.log(`⏱️ Starting OpenAI API call...`);

    try {
      // Test connectivity first
      console.log('🔍 Testing connectivity to OpenAI API...');
      try {
        const testResponse = await fetch('https://api.openai.com/v1/models', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${apiKey}`
          },
          signal: AbortSignal.timeout(5000) // 5 second test
        });
        console.log(`✅ Connectivity test: ${testResponse.status} ${testResponse.statusText}`);
      } catch (testError: any) {
        console.error(`❌ Connectivity test failed:`, {
          name: testError.name,
          message: testError.message,
          cause: testError.cause?.message
        });
        throw new Error(`Cannot connect to OpenAI API. This appears to be a network/firewall issue. Error: ${testError.message}`);
      }

      // Use fetch directly with AbortController for better timeout control
      const apiCallStart = Date.now();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
      
      try {
        console.log('📡 Making chat completion request...');
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: 'gpt-4o-mini',
            messages: messages,
            temperature: 0.7,
            max_tokens: 500
          }),
          signal: controller.signal
        });

        clearTimeout(timeoutId);
        
        console.log(`📥 Response received: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
          const errorText = await response.text();
          let errorData;
          try {
            errorData = JSON.parse(errorText);
          } catch {
            errorData = { raw: errorText };
          }
          throw new Error(`OpenAI API error: ${response.status} ${response.statusText} - ${JSON.stringify(errorData)}`);
        }

        const completion = await response.json();
        const apiCallDuration = Date.now() - apiCallStart;
        console.log(`⏱️ API call completed in ${apiCallDuration}ms`);

        const choice = completion.choices?.[0];
        if (!choice) {
          throw new Error('No completion choice returned from API');
        }
        
        const finalResponse = choice.message?.content || 'Sorry, I encountered an error.';
        
        console.log(`✅ Response: ${finalResponse.length} chars`);
        console.log(`⏱️ Total request time: ${Date.now() - startTime}ms`);

        return new Response(JSON.stringify({
          response: finalResponse
        }), {
          status: 200,
          headers: { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        console.error(`❌ Fetch error details:`, {
          name: fetchError.name,
          message: fetchError.message,
          cause: fetchError.cause?.message,
          stack: fetchError.stack?.substring(0, 300)
        });
        
        if (fetchError.name === 'AbortError') {
          throw new Error('Request timed out after 60 seconds');
        }
        
        if (fetchError.message?.includes('fetch failed') || fetchError.cause) {
          throw new Error(`Network error connecting to OpenAI API. This is likely a firewall, proxy, or connectivity issue. Original error: ${fetchError.message || fetchError.cause?.message || 'Unknown'}`);
        }
        
        throw fetchError;
      }
    } catch (apiError: any) {
      const duration = Date.now() - startTime;
      console.error(`❌ API error after ${duration}ms:`, {
        message: apiError.message,
        status: apiError.status,
        code: apiError.code,
        type: apiError.type
      });
      
      if (apiError.status === 401) {
        throw new Error('Invalid OpenAI API key');
      }
      
      if (apiError.message?.includes('timeout') || apiError.code === 'ECONNABORTED') {
        throw new Error(`OpenAI API timeout after ${duration}ms. This might be a network or API issue. Please try again.`);
      }
      
      throw apiError;
    }
  } catch (error: any) {
    const duration = Date.now() - startTime;
    console.error(`❌ Error after ${duration}ms:`, error.message);
    return new Response(JSON.stringify({ 
      error: error.message || 'An error occurred',
      duration: `${duration}ms`
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const OPTIONS: APIRoute = async () => {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
};