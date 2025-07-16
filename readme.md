# Natural Language SQL Query Generator

## Overview

This is a Streamlit-based application that allows users to query a SQLite database using natural language. The system converts user questions into SQL queries using OpenAI's API and displays the results with optional visualizations. The application provides a chat-like interface for database interaction without requiring SQL knowledge.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Components**: 
  - Main chat interface for natural language queries
  - Conversation history display with expandable query details
  - Data visualization using Plotly for charts and graphs
  - Session state management for conversation persistence

### Backend Architecture
- **Core Components**:
  - `SQLGenerator`: Handles natural language to SQL conversion using OpenAI API
  - `QueryExecutor`: Safely executes SQL queries with validation
  - `database.py`: Database initialization and metadata extraction
- **Architecture Pattern**: Modular design with clear separation of concerns

### Data Storage
- **Database**: SQLite with sample e-commerce data
- **Tables**: customers, products, orders, order_items
- **Data Management**: Automatic database initialization with sample data generation

## Key Components

### 1. SQL Generator (`sql_generator.py`)
- **Purpose**: Converts natural language questions to SQL queries
- **Technology**: OpenAI API integration
- **Features**: 
  - Context-aware query generation using conversation history
  - Database schema awareness for accurate query construction
  - Safety considerations for query generation

### 2. Query Executor (`query_executor.py`)
- **Purpose**: Safely executes SQL queries against the database
- **Security**: Only allows SELECT statements, blocks dangerous operations
- **Error Handling**: Comprehensive error handling for database and query execution errors
- **Output**: Returns results as pandas DataFrames

### 3. Database Module (`database.py`)
- **Purpose**: Database initialization and metadata extraction
- **Features**:
  - Automatic sample data generation for testing
  - Database schema introspection
  - E-commerce sample data (customers, products, orders)

### 4. Main Application (`app.py`)
- **Purpose**: Streamlit interface and application orchestration
- **Features**:
  - Session state management for conversation history
  - Visualization capabilities using Plotly
  - User interface for natural language queries

## Data Flow

1. **User Input**: User enters natural language question
2. **Context Building**: System builds context from conversation history and database metadata
3. **SQL Generation**: OpenAI API converts question to SQL query
4. **Query Validation**: System validates query safety (SELECT only)
5. **Query Execution**: Executor runs query against SQLite database
6. **Result Processing**: Results converted to pandas DataFrame
7. **Display**: Results shown in Streamlit interface with optional visualization
8. **History Storage**: Query and results stored in session state

## External Dependencies

### APIs
- **OpenAI API**: For natural language to SQL conversion
- **Configuration**: Requires `OPENAI_API_KEY` environment variable

### Python Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **SQLite3**: Database operations
- **OpenAI**: API client for GPT integration

## Deployment Strategy

### Development
- **Local Development**: Direct Python execution with Streamlit
- **Database**: SQLite file-based database (auto-generated)
- **Configuration**: Environment variables for API keys

### Production Considerations
- **Containerization**: Ready for Docker deployment
- **Scaling**: Stateless design suitable for horizontal scaling
- **Security**: Query validation prevents SQL injection
- **Monitoring**: Error handling and logging for production debugging

### Environment Setup
1. Install dependencies from requirements
2. Set `OPENAI_API_KEY` environment variable
3. Run `streamlit run app.py`
4. Database auto-initializes on first run

## Key Architectural Decisions

### SQLite Database Choice
- **Rationale**: Simplicity for demonstration and local development
- **Pros**: No external database server required, easy setup
- **Cons**: Limited scalability, single-user access
- **Alternative**: Could be extended to PostgreSQL for production

### OpenAI Integration
- **Rationale**: Leverages advanced language models for accurate SQL generation
- **Pros**: High-quality natural language understanding
- **Cons**: External API dependency, costs associated with usage
- **Alternative**: Local language models could be considered

### Security Model
- **Approach**: Whitelist approach allowing only SELECT queries
- **Rationale**: Prevents data modification and system compromise
- **Implementation**: Query validation before execution

### Session State Management
- **Approach**: Streamlit session state for conversation history
- **Rationale**: Provides context for follow-up questions
- **Limitation**: Memory-based, not persistent acros
