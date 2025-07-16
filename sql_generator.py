import json
import os
from openai import OpenAI

class SQLGenerator:
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY", "default_key")
        self.client = OpenAI(api_key=api_key)
    
    def generate_sql(self, user_question, database_metadata, conversation_history):
        """Generate SQL query based on user question and database metadata"""
        
        # Build context from conversation history
        context = ""
        if conversation_history:
            context = "\n\nPrevious conversation context:\n"
            for item in conversation_history[-3:]:  # Last 3 interactions
                context += f"Q: {item['question']}\n"
                context += f"SQL: {item['sql']}\n"
                if item['success']:
                    context += "Result: Success\n"
                else:
                    context += f"Result: Error - {item['error']}\n"
                context += "\n"
        
        # Build database schema description
        schema_description = self._build_schema_description(database_metadata)
        
        # Create the prompt
        prompt = f"""
You are an expert SQL query generator. Based on the user's natural language question and the database schema provided, generate a precise SQL query.

Database Schema:
{schema_description}

{context}

User Question: {user_question}

Instructions:
1. Generate only a valid SQL query that answers the user's question
2. Use proper SQL syntax for SQLite
3. Consider the conversation context for follow-up questions
4. Use appropriate JOINs when data spans multiple tables
5. Include proper WHERE clauses for filtering
6. Use aggregation functions when appropriate
7. Ensure the query is safe and follows best practices
8. Do not include any explanation, just the SQL query

Respond with a JSON object containing only the SQL query:
{{"sql": "your_sql_query_here"}}
"""
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL query generator. Always respond with valid JSON containing only the SQL query."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("sql", "").strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate SQL query: {str(e)}")
    
    def _build_schema_description(self, metadata):
        """Build a readable schema description"""
        schema_parts = []
        
        for table_name, table_info in metadata.items():
            schema_parts.append(f"\nTable: {table_name}")
            schema_parts.append("Columns:")
            
            for col_name, col_info in table_info['columns'].items():
                col_desc = f"  - {col_name}: {col_info['type']}"
                if col_info['primary_key']:
                    col_desc += " (PRIMARY KEY)"
                if not col_info['nullable']:
                    col_desc += " (NOT NULL)"
                schema_parts.append(col_desc)
            
            # Add sample data
            if 'sample_data' in table_info and table_info['sample_data']:
                schema_parts.append("Sample data:")
                for row in table_info['sample_data']:
                    schema_parts.append(f"  {row}")
        
        return "\n".join(schema_parts)
