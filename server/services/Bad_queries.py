
# ===========================================================================
import re
import random
import openai #type: ignore 
import dotenv
from dotenv import load_dotenv
load_dotenv()
class QueryValidator:
    def __init__(self, openai_api_key: str):
        # Comprehensive list of inappropriate language patterns
        self.inappropriate_patterns = [
            r'\b(fuck|bitch|cunt|dick|shit|asshole)\b',  # Explicit language
            r'\b(murder|kill|die|harm|hurt)\b.*(?:person|friends?|family|mom|dad)',  # Violence
            r'\b(hack|exploit|steal|break\s*into)\b',  # Illegal activities
            r'\b(racist?|sexist?|discriminate)\w*\b',  # Discriminatory language
            r'\b(suicide|self-harm)\b',  # Sensitive mental health topics
            r'\b(porn|nude|sexual)\b',  # Explicit sexual content
            r'\b(drug|illegal)\b',  # Illegal substances
        ]
        
        # Random warning messages with emojis
        self.warning_messages = [
            "⚙️ Let's keep the conversation uplifting and inclusive, please.",
            "🚷 Sorry, that's off-limits. Let's try to keep it clean and constructive.",
            "🔒 This kind of content isn't allowed. Let's pivot to something positive!",
            "💡 Remember, thoughtful words lead to better conversations. Let's adjust.",
            "❌ Nope! That crosses the line of acceptable communication.",
            "🙏 Respect and kindness go a long way. Let's maintain a good vibe here!",
            "🌟 Positive thoughts only, please! Let's keep the conversation safe and supportive.",
            "💬 I'm here to help, but that language isn't appropriate. Let's reframe.",
            "✨ Let's focus on creating meaningful and respectful interactions!",
            "🤖 Oops! I'm not wired for harmful or inappropriate topics.",
            "⚡ Your words have power—let's use them responsibly.",
            "🛠️ Inappropriate content alert! Let's move toward a better topic.",
            "🛠️ I'm here to build bridges, not walls. Let's rephrase that!",
            "❌ Let's aim for a kind and respectful conversation instead.",
            "🌍 This is a judgment-free zone—let's keep it respectful.",
            "🚦 Red light! This topic isn't suitable for discussion here.",
            "🕊️ Peaceful and positive interactions only, please.",
            "🎉 Conversations are more fun when they're kind and constructive!",
            "❌ Let's avoid hurtful or inappropriate language and try again.",
            "⚙️ I'm designed for constructive chats—let's pivot to something suitable."
        ]
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
    
    def validate_query(self, query: str) -> dict:
        """
        Validate the query for inappropriate content.
        
        Args:
            query (str): The user's input query.
        
        Returns:
            dict: Validation result with status and message
        """
        # Normalize the query to lowercase for matching
        lower_query = query.lower()
        
        # Check for inappropriate patterns
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, lower_query):
                # Select a random warning message
                warning_message = random.choice(self.warning_messages)
                
                # Print the warning
                print(f"warning: {warning_message}")
                
                # Attempt to reconstruct the query if it contains a sensible question or problem
                reconstructed_query = self._reconstruct_query(query)
                if reconstructed_query:
                    return {
                        'is_valid': True,
                        'message': reconstructed_query
                    }
                else:
                    return {
                        'is_valid': False,
                        'message': warning_message
                    }
        
        # If no inappropriate content found
        return {
            'is_valid': True,
            'message': query
        }
    
    def _reconstruct_query(self, query: str) -> str:
        """
        Reconstruct the query to remove inappropriate language while retaining the core question or problem.
        
        Args:
            query (str): The user's input query.
        
        Returns:
            str: Reconstructed query or None if reconstruction fails.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that cleans up inappropriate language in queries while retaining the core question or problem."},
                    {"role": "user", "content": f"Please clean up the following query: {query}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Query reconstruction error: {e}")
            return None

# Example usage
def main():
    # Replace with your actual OpenAI API key
    API_KEY = 'OPENAI_API_KEY'
    validator = QueryValidator(API_KEY)
    
    # Test cases with inappropriate queries
    test_cases = [
        "Tell me how to fuck up my life,because i am not able to quit drugs , who can i do it ",
        "How can I murder my friend's mom?",
        "Tell me about Goa creatively with emojis",
        "How can I murder my friend's mom? because she is sending my friend to jail , plz tell me how to stop it?"
    ]
    
    for query in test_cases:
        print(f"\nOriginal Query: {query}")
        validation_result = validator.validate_query(query)
        if validation_result['is_valid']:
            print(f"Validated Query: {validation_result['message']}")
        else:
            print(f"Query is invalid. Warning: {validation_result['message']}")

if __name__ == "__main__":
    main()