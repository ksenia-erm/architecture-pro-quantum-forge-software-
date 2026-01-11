import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag_bot import RAGbot

# TELEGRAM BOT CONFIGURATION
TELEGRAM_TOKEN = "8467679077:AAFDUMUBes5IBSVMK0aflrdieyd4lTDMUGU"
CHAT_MEMORY_LIMIT = 5  # Сообщения в истории

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramRAGBot:
    def __init__(self, token: str, chroma_path: str = "../chroma_db"):
        # Step 1: Initialize RAG core
        self.rag_core = RAGbot(chroma_path=chroma_path)
        self.token = token

        # Step 2: Chat history (user_id -> list of messages)
        self.chat_history = {}

        print(f"✅ TelegramRAGBot initialized!")
        print(f"📊 RAG Index: {self.rag_core.vectorstore._collection.count()} documents")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🚀 **Hogwarts Knowledge RAG Bot**

Ask me anything about:
• Alaric Pendragon
• Battle of Astronomy Tower  
• Marcus Thornfield
• Elena Blackwell

*Examples:*
`/ask Who killed Alaric Pendragon?`
`What did Marcus do after Pendragon's death?`

**Type /help for commands**
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**Commands:**
• `/start` - Show welcome message
• `/help` - Show this help
• `/status` - Check index status
• `/clear` - Clear chat history
• `/ask <question>` - Ask RAG question

**Just type your question** for normal chat!
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show index statistics"""
        doc_count = self.rag_core.vectorstore._collection.count()
        await update.message.reply_text(
            f"📊 **Index Status**\n"
            f"Documents: *{doc_count}*\n"
            f"Model: `llama3.2:3b`\n"
            f"Embeddings: `all-MiniLM-L6-v2`",
            parse_mode='Markdown'
        )

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear chat history for user"""
        user_id = update.effective_user.id
        self.chat_history[user_id] = []
        await update.message.reply_text("🗑️ Chat history cleared!")

    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command"""
        if not context.args:
            await update.message.reply_text("❓ Usage: `/ask Who is Alaric Pendragon?`")
            return

        question = " ".join(context.args)
        await self.handle_query(update, question)

    async def handle_query(self, update: Update, question: str):
        """Core query handler"""
        user_id = update.effective_user.id

        # Add to history
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
        self.chat_history[user_id].append(f"Q: {question}")

        # Limit history
        if len(self.chat_history[user_id]) > CHAT_MEMORY_LIMIT * 2:
            self.chat_history[user_id] = self.chat_history[user_id][-CHAT_MEMORY_LIMIT * 2:]

        # Show typing indicator
        await update.message.reply_chat_action("typing")

        try:
            # RAG query
            answer = self.rag_core.query(question)

            # Add to history
            self.chat_history[user_id].append(f"A: {answer}")

            # Send response
            await update.message.reply_text(answer, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Query error: {e}")
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n\nTry `/status` to check index"
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        question = update.message.text.strip()
        await self.handle_query(update, question)

    def run(self):
        """Start Telegram bot"""
        # Create application
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("clear", self.clear_history))
        application.add_handler(CommandHandler("ask", self.ask_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("🤖 Telegram bot starting...")
        print("💬 Send /start to your bot!")

        # Run bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

# Main execution
if __name__ == "__main__":
    if TELEGRAM_TOKEN == "":
        print("❌ ERROR: Set your TELEGRAM_TOKEN!")
        print("1. Message @BotFather in Telegram")
        print("2. /newbot → Create bot")
        print("3. Copy token → Paste in BOT_TOKEN")
        exit(1)

    # Initialize and run
    bot = TelegramRAGBot(TELEGRAM_TOKEN)
    bot.run()
