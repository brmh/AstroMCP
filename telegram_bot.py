import logging
import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from datetime import datetime
import swisseph as swe

# Import project logic
from api.config import settings
from api.dependencies import birth_data_to_jd, geocode_city
from api.core.charts import build_natal_chart
from api.models.request_models import BirthData, NatalChartOptions, Ayanamsa

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
TOKEN = "8695301995:AAHfjlvE2ma3jF9LX5-R-YgQUJ2ejH5uqgY"

# Conversation states
NAME, DATE, TIME, LOCATION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"नमस्ते {user.mention_html()}! I am your AI Astrology Consultant. "
        "I can generate your Vedic Kundli. Use /kundli to start."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Use /kundli to generate your birth chart.")

async def kundli_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the Kundli conversation."""
    await update.message.reply_text("Let's generate your Kundli. What is your name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Nice to meet you, {update.message.text}. What is your birth date? (DD-MM-YYYY)")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str = update.message.text
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        context.user_data['date'] = date_str
        await update.message.reply_text("Got it. What is your birth time? (HH:MM in 24-hour format)")
        return TIME
    except ValueError:
        await update.message.reply_text("Invalid format. Please use DD-MM-YYYY (e.g., 25-12-1990).")
        return DATE

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text
    try:
        datetime.strptime(time_str, "%H:%M")
        context.user_data['time'] = time_str
        await update.message.reply_text("And your birth city? (e.g., Delhi, India)")
        return LOCATION
    except ValueError:
        await update.message.reply_text("Invalid format. Please use HH:MM (e.g., 14:30).")
        return TIME

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    await update.message.reply_text(f"Calculating for {city}...")
    
    try:
        geo = geocode_city(city)
        name = context.user_data['name']
        date_parts = list(map(int, context.user_data['date'].split('-')))
        time_parts = list(map(int, context.user_data['time'].split(':')))
        
        # Build BirthData model
        birth_data = BirthData(
            name=name,
            birth_year=date_parts[2],
            birth_month=date_parts[1],
            birth_day=date_parts[0],
            birth_hour=time_parts[0],
            birth_minute=time_parts[1],
            birth_second=0,
            latitude=geo['latitude'],
            longitude=geo['longitude'],
            timezone=geo['timezone']
        )
        
        # Initialize Swiss Ephemeris if not already
        swe.set_ephe_path(settings.EPHE_PATH)
        
        jd = birth_data_to_jd(birth_data)
        chart = build_natal_chart(
            jd, geo['latitude'], geo['longitude'], 
            house_system="WHOLE_SIGN",
            zodiac_type="SIDEREAL", 
            ayanamsa=Ayanamsa.LAHIRI.value
        )
        
        # Format output
        response = f"✨ *Vedic Kundli for {name}* ✨\n\n"
        response += f"📍 Location: {geo['display_name']}\n"
        response += f"🕒 Timezone: {geo['timezone']}\n\n"
        
        response += "*Planet Positions:*\n"
        for planet, info in chart.get('planets', {}).items():
            response += f"• {planet.capitalize()}: {info['sign']} ({info['house']} House)\n"
        
        response += f"\n🌅 Ascendant: {chart.get('houses', {}).get('ascendant_sign', 'N/A')}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error generating kundli: {e}")
        await update.message.reply_text(f"Sorry, I encountered an error: {str(e)}")
        
    return ConversationFactory.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chat ended. Use /kundli to start again.", reply_markup=ReplyKeyboardRemove())
    return ConversationFactory.END

if __name__ == '__main__':
    # Set ephemeris path for local testing
    swe.set_ephe_path(settings.EPHE_PATH)
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('kundli', kundli_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    
    logger.info("Bot starting...")
    application.run_polling()
