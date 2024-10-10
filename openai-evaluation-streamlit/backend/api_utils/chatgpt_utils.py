import logging
import openai
from openai.error import OpenAIError, AuthenticationError, RateLimitError, APIConnectionError

# Initialize logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

# Configuration for response limits
MAX_SENTENCES = 10
MAX_WORDS = 200
MAX_TOKENS = 300

# Initialize OpenAI API using the provided API key
def init_openai(api_key):
    """
    Initializes the OpenAI API with the provided API key.
    Raises an error if the API key is not provided.
    """
    if not api_key:
        raise ValueError("OpenAI API key not provided.")
    
    openai.api_key = api_key
    logger.info("OpenAI API initialized")

# Function to send a question and preprocessed file data to ChatGPT
def get_chatgpt_response(question, model_name="gpt-3.5-turbo", instructions=None, preprocessed_data=None):
    # Construct the system message for the Chat API
    system_message = {
        "role": "system",
        "content": (
            "You are an AI assistant specialized in providing concise, accurate answers. "
            "Focus on the key information requested without adding unnecessary context. "
            "Use any provided instructions or reference data to inform your answer."
        )
    }

    # Construct the user message, include instructions or preprocessed_data only if they exist
    user_message = f"Question: {question}\n"
    
    if instructions:
        user_message += f"Instructions: {instructions}\n"
    
    if preprocessed_data:
        user_message += f"Reference Data: {preprocessed_data}\n"

    user_message += (
        "Please provide a concise answer that directly addresses the question. Your response should:\n"
        f"1. Be no longer than {MAX_SENTENCES} sentences or {MAX_WORDS} words, whichever is shorter.\n"
        "2. Include only essential information relevant to the question.\n"
        "3. Use precise language and avoid unnecessary elaboration.\n"
        "4. If using reference data, integrate it seamlessly without mentioning the source.\n"
    )

    logger.debug(f"Sending question to ChatGPT using model {model_name}: {user_message}")

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[system_message, {"role": "user", "content": user_message}],
            temperature=0.2,
            max_tokens=MAX_TOKENS,  # Updated max_tokens to 300 to allow 200 words
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        
        answer = response['choices'][0]['message']['content'].strip()
        sentences = answer.split('.')
        words = answer.split()

        if len(sentences) > MAX_SENTENCES:
            answer = '. '.join(sentences[:MAX_SENTENCES]) + '.'
        if len(words) > MAX_WORDS:
            answer = ' '.join(words[:MAX_WORDS]) + '...'

        logger.debug(f"ChatGPT Response: {answer.strip()}")
        return answer.strip(), model_name  # Also return model name to store in database

    except (AuthenticationError, RateLimitError, APIConnectionError) as e:
        logger.error(f"OpenAI specific error: {e}")
        return f"Error: {e.user_message}", model_name

    except OpenAIError as e:
        logger.error(f"General OpenAI API error: {e}")
        return "An error occurred while processing the request. Please try again later.", model_name

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please contact support.", model_name


# Compare ChatGPT's response with the expected answer using OpenAI API
def compare_and_update_status(row, chatgpt_response, instructions):
    original_answer = str(row['FinalAnswer']).strip()
    ai_engine_answer = chatgpt_response.strip()
    question = row['Question'].strip()

    # Construct a comparison prompt for OpenAI
    comparison_prompt = f"""
Question: {question}

Original Answer: {original_answer}

AI Response: {ai_engine_answer}

Instructions:
1. Analyze if the AI's response contains the key information present in the original answer.
2. Focus on factual accuracy and relevance to the question.
3. Ignore minor differences in phrasing or additional context.
4. Respond with 'YES' if the core information matches, 'NO' if it doesn't.

Does the AI's response match the key information in the original answer? Respond with only 'YES' or 'NO'.
"""

    logger.debug(f"Sending comparison prompt to ChatGPT:\n{comparison_prompt}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": comparison_prompt}],
            temperature=0
        )
        
        comparison_result = response['choices'][0]['message']['content'].strip().lower()
        logger.debug(f"Comparison Result:\n{comparison_result}")
        if 'yes' in comparison_result:
            return 'Correct with Instruction' if instructions else 'Correct without Instruction'
        elif 'no' in comparison_result:
            return 'Incorrect with Instruction' if instructions else 'Incorrect without Instruction'
        else:
            logger.error(f"Unexpected response from OpenAI: {comparison_result}")
            return 'Error'

    except (AuthenticationError, RateLimitError, APIConnectionError) as e:
        logger.error(f"OpenAI specific error during comparison: {e}")
        return "Error: OpenAI service is currently unavailable."

    except OpenAIError as e:
        logger.error(f"General OpenAI API error during comparison: {e}")
        return 'Error'

    except Exception as e:
        logger.error(f"Unexpected error during comparison: {e}")
        return 'Error'
