import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import initialize_database, get_database_metadata
from sql_generator import SQLGenerator
from query_executor import QueryExecutor

# Initialize database and components
@st.cache_resource
def setup_components():
    """Initialize database and core components"""
    db_path = initialize_database()
    metadata = get_database_metadata(db_path)
    sql_generator = SQLGenerator()
    query_executor = QueryExecutor(db_path)
    return sql_generator, query_executor, metadata

def initialize_session_state():
    """Initialize session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'query_results' not in st.session_state:
        st.session_state.query_results = None
    if 'last_sql' not in st.session_state:
        st.session_state.last_sql = None

def display_conversation_history():
    """Display the conversation history"""
    if st.session_state.conversation_history:
        st.subheader("Conversation History")
        for i, item in enumerate(st.session_state.conversation_history):
            with st.expander(f"Query {i+1}: {item['question'][:50]}..."):
                st.write("**Question:**", item['question'])
                st.write("**Generated SQL:**")
                st.code(item['sql'], language='sql')
                if item['success']:
                    st.write("**Results:**")
                    if isinstance(item['result'], pd.DataFrame) and not item['result'].empty:
                        st.dataframe(item['result'])
                    else:
                        st.write("No results returned")
                else:
                    st.error(f"Error: {item['error']}")

def create_visualization(df, query):
    """Create appropriate visualization based on the data"""
    if df.empty:
        return None
    
    # Simple heuristics for chart type selection
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        # Bar chart for categorical vs numeric
        fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], 
                     title=f"{numeric_cols[0]} by {categorical_cols[0]}")
        return fig
    elif len(numeric_cols) >= 2:
        # Scatter plot for numeric vs numeric
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                        title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
        return fig
    elif len(numeric_cols) == 1:
        # Histogram for single numeric column
        fig = px.histogram(df, x=numeric_cols[0], 
                          title=f"Distribution of {numeric_cols[0]}")
        return fig
    
    return None

def display_sample_queries():
    """Display sample queries to help users get started"""
    st.subheader("Sample Queries")
    sample_queries = [
        "Show me all customers from New York",
        "What are the top 5 products by total sales?",
        "How many orders were placed in the last month?",
        "Show me the average order value by customer city",
        "Which products have never been ordered?"
    ]
    
    cols = st.columns(len(sample_queries))
    for i, query in enumerate(sample_queries):
        with cols[i]:
            if st.button(query, key=f"sample_{i}"):
                st.session_state.sample_query = query
                st.rerun()

def main():
    st.set_page_config(
        page_title="SQL Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Natural Language to SQL Chatbot")
    st.markdown("Ask questions about your data in plain English, and I'll generate SQL queries to get the answers!")
    
    # Initialize components
    sql_generator, query_executor, metadata = setup_components()
    initialize_session_state()
    
    # Sidebar with database schema
    with st.sidebar:
        st.header("Database Schema")
        st.json(metadata)
        
        # Clear conversation button
        if st.button("Clear Conversation"):
            st.session_state.conversation_history = []
            st.session_state.query_results = None
            st.session_state.last_sql = None
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display sample queries
        display_sample_queries()
        
        # User input
        user_input = st.text_area(
            "Ask your question:",
            value=st.session_state.get('sample_query', ''),
            height=100,
            placeholder="e.g., Show me the top 10 customers by total order value"
        )
        
        # Clear the sample query from session state
        if 'sample_query' in st.session_state:
            del st.session_state.sample_query
        
        if st.button("Generate Query", type="primary"):
            if user_input.strip():
                with st.spinner("Generating SQL query..."):
                    try:
                        # Generate SQL
                        sql_query = sql_generator.generate_sql(user_input, metadata, 
                                                             st.session_state.conversation_history)
                        
                        st.session_state.last_sql = sql_query
                        
                        # Display generated SQL
                        st.subheader("Generated SQL:")
                        st.code(sql_query, language='sql')
                        
                        # Execute query
                        with st.spinner("Executing query..."):
                            try:
                                result_df = query_executor.execute_query(sql_query)
                                st.session_state.query_results = result_df
                                
                                # Add to conversation history
                                st.session_state.conversation_history.append({
                                    'question': user_input,
                                    'sql': sql_query,
                                    'result': result_df,
                                    'success': True,
                                    'error': None
                                })
                                
                                st.success("Query executed successfully!")
                                
                            except Exception as e:
                                error_msg = str(e)
                                st.error(f"Error executing query: {error_msg}")
                                
                                # Add failed query to history
                                st.session_state.conversation_history.append({
                                    'question': user_input,
                                    'sql': sql_query,
                                    'result': None,
                                    'success': False,
                                    'error': error_msg
                                })
                                
                    except Exception as e:
                        st.error(f"Error generating SQL: {str(e)}")
            else:
                st.warning("Please enter a question.")
    
    with col2:
        # Display query results
        if st.session_state.query_results is not None:
            st.subheader("Query Results")
            df = st.session_state.query_results
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Show basic statistics
                st.write(f"**Rows returned:** {len(df)}")
                
                # Create visualization if appropriate
                fig = create_visualization(df, st.session_state.last_sql)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results returned from the query.")
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("---")
        display_conversation_history()

if __name__ == "__main__":
    main()
