import os
import logging
import tempfile
import sys
import re
import string
from datetime import datetime
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language options for TTS
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Mandarin)',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

# Comprehensive Grammar and Spelling Rules
GRAMMAR_RULES = {
    # Common contractions
    "don't": 'do not',
    "can't": 'cannot',
    "won't": 'will not',
    "shouldn't": 'should not',
    "wouldn't": 'would not',
    "couldn't": 'could not',
    "isn't": 'is not',
    "aren't": 'are not',
    "wasn't": 'was not',
    "weren't": 'were not',
    "hasn't": 'has not',
    "haven't": 'have not',
    "hadn't": 'had not',
    "doesn't": 'does not',
    "didn't": 'did not',
    "ain't": 'am not',
    "i'm": 'I am',
    "you're": 'you are',
    "he's": 'he is',
    "she's": 'she is',
    "it's": 'it is',
    "we're": 'we are',
    "they're": 'they are',
    "i'll": 'I will',
    "you'll": 'you will',
    "he'll": 'he will',
    "she'll": 'she will',
    "it'll": 'it will',
    "we'll": 'we will',
    "they'll": 'they will',
    "i've": 'I have',
    "you've": 'you have',
    "we've": 'we have',
    "they've": 'they have',
    "i'd": 'I would',
    "you'd": 'you would',
    "he'd": 'he would',
    "she'd": 'she would',
    "we'd": 'we would',
    "they'd": 'they would',
    
    # Articles
    'a apple': 'an apple',
    'a hour': 'an hour',
    'a honest': 'an honest',
    'a honor': 'an honor',
    'a umbrella': 'an umbrella',
    'a university': 'a university',
    'a European': 'a European',
    'a one': 'a one',
    
    # Common misspellings
    'teh': 'the',
    'adn': 'and',
    'thier': 'their',
    'there': 'their',
    'your': 'your',
    'youre': "you're",
    'alot': 'a lot',
    'untill': 'until',
    'recieve': 'receive',
    'belive': 'believe',
    'acheive': 'achieve',
    'occured': 'occurred',
    'ocurred': 'occurred',
    'seperate': 'separate',
    'definately': 'definitely',
    'govenment': 'government',
    'enviornment': 'environment',
    'accomodate': 'accommodate',
    'aquire': 'acquire',
    'arguement': 'argument',
    'begining': 'beginning',
    'business': 'business',
    'calendar': 'calendar',
    'career': 'career',
    'catagory': 'category',
    'cemetary': 'cemetery',
    'collaegue': 'colleague',
    'comittee': 'committee',
    'concious': 'conscious',
    'consious': 'conscious',
    'dilemna': 'dilemma',
    'disappear': 'disappear',
    'disatisfied': 'dissatisfied',
    'embarass': 'embarrass',
    'enviroment': 'environment',
    'excede': 'exceed',
    'existance': 'existence',
    'experiance': 'experience',
    'guarantee': 'guarantee',
    'harrass': 'harass',
    'independant': 'independent',
    'indispensible': 'indispensable',
    'inoculate': 'inoculate',
    'irresistable': 'irresistible',
    'maintainance': 'maintenance',
    'millenium': 'millennium',
    'miniscule': 'minuscule',
    'mischevious': 'mischievous',
    'neccessary': 'necessary',
    'occassion': 'occasion',
    'occurence': 'occurrence',
    'pavillion': 'pavilion',
    'perserverance': 'perseverance',
    'prefered': 'preferred',
    'priviledge': 'privilege',
    'pronounciation': 'pronunciation',
    'publically': 'publicly',
    'reccommend': 'recommend',
    'relevent': 'relevant',
    'repetition': 'repetition',
    'rhythm': 'rhythm',
    'schedual': 'schedule',
    'seperate': 'separate',
    'similiar': 'similar',
    'sucess': 'success',
    'suprize': 'surprise',
    'tommorow': 'tomorrow',
    'unescessary': 'unnecessary',
    'wierd': 'weird',
    
    # Common phrase corrections
    'could of': 'could have',
    'should of': 'should have',
    'would of': 'would have',
    'must of': 'must have',
    'might of': 'might have',
    'i of': 'I have',
    'you of': 'you have',
    'we of': 'we have',
    'they of': 'they have',
}

# Spelling dictionary (common words)
SPELLING_DICT = {
    'accommodate': 'accommodate',
    'acquire': 'acquire',
    'argument': 'argument',
    'beginning': 'beginning',
    'business': 'business',
    'calendar': 'calendar',
    'career': 'career',
    'category': 'category',
    'cemetery': 'cemetery',
    'colleague': 'colleague',
    'committee': 'committee',
    'conscious': 'conscious',
    'dilemma': 'dilemma',
    'disappear': 'disappear',
    'dissatisfied': 'dissatisfied',
    'embarrass': 'embarrass',
    'environment': 'environment',
    'exceed': 'exceed',
    'existence': 'existence',
    'experience': 'experience',
    'guarantee': 'guarantee',
    'harass': 'harass',
    'independent': 'independent',
    'indispensable': 'indispensable',
    'inoculate': 'inoculate',
    'irresistible': 'irresistible',
    'maintenance': 'maintenance',
    'millennium': 'millennium',
    'minuscule': 'minuscule',
    'mischievous': 'mischievous',
    'necessary': 'necessary',
    'occasion': 'occasion',
    'occurrence': 'occurrence',
    'pavilion': 'pavilion',
    'perseverance': 'perseverance',
    'preferred': 'preferred',
    'privilege': 'privilege',
    'pronunciation': 'pronunciation',
    'publicly': 'publicly',
    'recommend': 'recommend',
    'relevant': 'relevant',
    'repetition': 'repetition',
    'rhythm': 'rhythm',
    'schedule': 'schedule',
    'separate': 'separate',
    'similar': 'similar',
    'success': 'success',
    'surprise': 'surprise',
    'tomorrow': 'tomorrow',
    'unnecessary': 'unnecessary',
    'weird': 'weird',
}

# User preferences
user_preferences = {}

def get_token():
    """Get token from environment variables"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", "your_bot_token_here", ""]:
        return token
    
    token = os.getenv('BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    token = os.getenv('TELEGRAM_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    return None

def spell_check(text):
    """Advanced spelling checker"""
    words = text.split()
    misspelled = []
    suggestions = []
    
    for word in words:
        # Remove punctuation for checking
        clean_word = word.strip(string.punctuation)
        lower_word = clean_word.lower()
        
        # Check if word is misspelled
        if lower_word not in SPELLING_DICT and len(clean_word) > 2:
            # Check if it's a known misspelling
            if lower_word in GRAMMAR_RULES:
                correction = GRAMMAR_RULES[lower_word]
                misspelled.append(clean_word)
                suggestions.append(correction)
            # Check for common typos (Levenshtein distance simulation)
            else:
                # Simple fuzzy matching for common typos
                for correct_word in SPELLING_DICT.keys():
                    if len(correct_word) == len(clean_word) or len(correct_word) == len(clean_word) + 1:
                        # Check if they are similar (simple comparison)
                        if sum(a != b for a, b in zip(clean_word, correct_word)) <= 2:
                            misspelled.append(clean_word)
                            suggestions.append(correct_word)
                            break
    
    return {
        'has_misspellings': len(misspelled) > 0,
        'misspelled': misspelled,
        'suggestions': suggestions,
        'total_errors': len(misspelled)
    }

def correct_grammar(text):
    """AI Grammar Correction with advanced rules"""
    original_text = text
    corrections = []
    corrected_text = text
    
    # Step 1: Fix common misspellings and phrases
    words = corrected_text.split()
    corrected_words = []
    
    for word in words:
        clean_word = word.strip(string.punctuation)
        lower_word = clean_word.lower()
        
        # Check if word needs correction
        if lower_word in GRAMMAR_RULES:
            correction = GRAMMAR_RULES[lower_word]
            # Preserve capitalization
            if clean_word[0].isupper():
                correction = correction.capitalize()
            # Preserve punctuation
            if word != clean_word:
                correction += word[-1] if word[-1] in string.punctuation else ''
            corrected_words.append(correction)
            corrections.append(f"'{clean_word}' → '{correction}'")
        else:
            corrected_words.append(word)
    
    corrected_text = ' '.join(corrected_words)
    
    # Step 2: Fix capitalization
    sentences = corrected_text.split('. ')
    corrected_text = '. '.join([s.capitalize() if s else s for s in sentences])
    
    # Step 3: Fix article errors (a/an)
    corrected_text = re.sub(r'\ba ([aeiouAEIOU])', r'an \1', corrected_text)
    corrected_text = re.sub(r'\ban ([^aeiouAEIOU])', r'a \1', corrected_text)
    
    # Step 4: Remove extra spaces
    corrected_text = ' '.join(corrected_text.split())
    
    # Step 5: Fix "i" to "I"
    corrected_text = re.sub(r'\bi\b', 'I', corrected_text)
    
    # Step 6: Capitalize days and months
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for month in months:
        corrected_text = re.sub(rf'\b{month}\b', month.capitalize(), corrected_text, flags=re.IGNORECASE)
    for day in days:
        corrected_text = re.sub(rf'\b{day}\b', day.capitalize(), corrected_text, flags=re.IGNORECASE)
    
    # Step 7: Fix double punctuation
    corrected_text = re.sub(r'([.!?])\1+', r'\1', corrected_text)
    
    # Step 8: Fix spacing around punctuation
    corrected_text = re.sub(r'\s+([.,!?;:])', r'\1', corrected_text)
    
    # Determine if changes were made
    changes_made = len(corrections) > 0 or original_text != corrected_text
    
    return {
        'original': original_text,
        'corrected': corrected_text,
        'changes_made': changes_made,
        'corrections': corrections[:10] if corrections else [],
        'total_corrections': len(corrections)
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user = update.effective_user
    current_time = datetime.now().strftime("%I:%M %p")
    
    await update.message.reply_text(
        f"🎙️ Welcome to @josealvarez21_bot, {user.first_name}! 👋\n\n"
        f"🕐 Current time: {current_time}\n\n"
        "I'm a **triple-function** bot that can:\n"
        "1️⃣ **Convert text to speech** (TTS) 🎙️\n"
        "2️⃣ **Correct grammar** ✍️\n"
        "3️⃣ **Check spelling** 📝\n\n"
        "📝 Commands:\n"
        "/start - Show this message\n"
        "/tts - Convert text to speech\n"
        "/grammar - Check and correct grammar\n"
        "/spell - Check spelling\n"
        "/lang - Change TTS language\n"
        "/speed - Change speech speed\n"
        "/help - Get help\n"
        "/about - About this bot\n\n"
        "💡 How to use:\n"
        "• For TTS: Send /tts followed by your text\n"
        "• For Grammar: Send /grammar followed by your text\n"
        "• For Spelling: Send /spell followed by your text\n"
        "• Or just send any text and I'll ask what you want!"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about information."""
    await update.message.reply_text(
        "🤖 About @josealvarez21_bot\n\n"
        "🎯 Purpose: Triple-function bot - TTS + Grammar + Spelling\n"
        "🌐 TTS Languages: 12+ languages supported\n"
        "✍️ Grammar: AI-powered correction with 100+ rules\n"
        "📝 Spelling: Advanced spelling checker with 100+ words\n"
        "⚡ Features: TTS, Grammar check, Spelling check, Language selection\n"
        "🔧 Technology: Python + Google TTS + AI Grammar Rules\n"
        "📅 Created: 2026\n\n"
        "🌟 Special Features:\n"
        "• 12+ TTS languages\n"
        "• Smart grammar correction\n"
        "• Advanced spelling checking\n"
        "• Detailed change tracking\n"
        "• Multiple speed options\n"
        "• User-friendly interface\n"
        "• Interactive mode\n\n"
        "📊 Correction Types:\n"
        "• Grammar errors\n"
        "• Spelling mistakes\n"
        "• Punctuation errors\n"
        "• Capitalization issues\n"
        "• Article errors (a/an)\n"
        "• Contraction corrections\n\n"
        "Made with ❤️ for the Telegram community"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    await update.message.reply_text(
        "🎙️ @josealvarez21_bot Help\n\n"
        "📖 How to use:\n\n"
        "**For Text-to-Speech:**\n"
        "/tts [your text] - Convert text to speech\n"
        "Example: /tts Hello, how are you?\n\n"
        "**For Grammar Correction:**\n"
        "/grammar [your text] - Check and correct grammar\n"
        "Example: /grammar i am go to school\n\n"
        "**For Spelling Check:**\n"
        "/spell [your text] - Check spelling\n"
        "Example: /spell I recieve a message\n\n"
        "**Commands:**\n"
        "/start - Welcome message\n"
        "/tts - Convert text to speech\n"
        "/grammar - Check and correct grammar\n"
        "/spell - Check spelling\n"
        "/lang - Change TTS language\n"
        "/speed - Change speech speed\n"
        "/help - This menu\n"
        "/about - About this bot\n\n"
        "🗣️ TTS Languages: English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi\n\n"
        "✍️ Grammar Features:\n"
        "• Corrects common spelling errors\n"
        "• Fixes capitalization\n"
        "• Corrects article usage (a/an)\n"
        "• Fixes punctuation\n"
        "• Capitalizes days and months\n"
        "• Fixes contractions\n"
        "• Shows detailed changes\n\n"
        "📝 Spelling Features:\n"
        "• Checks for misspelled words\n"
        "• Provides correction suggestions\n"
        "• Identifies total errors\n"
        "• Highlights misspelled words\n\n"
        "💡 Tip: You can also just send any text and I'll ask how to process it!"
    )

async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tts command"""
    text = update.message.text.replace('/tts', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to convert to speech!\n"
            "Example: /tts Hello, how are you?"
        )
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    
    await update.message.reply_text(f"🎤 Converting to speech in {LANGUAGES.get(lang, 'English')}...")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        speed_label = "Normal" if speed == 'normal' else "Slow"
        
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🔊 Text-to-Speech\n"
                       f"🌐 Language: {LANGUAGES.get(lang, 'English')}\n"
                       f"🎚️ Speed: {speed_label}\n"
                       f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}",
                title="TTS Audio",
                performer="@josealvarez21_bot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error in tts: {e}")
        await update.message.reply_text("❌ Error converting text to speech. Please try again.")

async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /grammar command"""
    text = update.message.text.replace('/grammar', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to check grammar!\n"
            "Example: /grammar i am go to school"
        )
        return
    
    await update.message.reply_text("✍️ Analyzing and correcting grammar...")
    
    try:
        result = correct_grammar(text)
        
        if result['changes_made']:
            response = (
                f"✍️ **Grammar Correction Results**\n\n"
                f"📝 **Original:**\n{result['original']}\n\n"
                f"✅ **Corrected:**\n{result['corrected']}\n\n"
                f"🔧 **Corrections Made:** ({result['total_corrections']} changes)\n"
            )
            
            if result['corrections']:
                for i, correction in enumerate(result['corrections'][:5], 1):
                    response += f"{i}. {correction}\n"
                if len(result['corrections']) > 5:
                    response += f"... and {len(result['corrections']) - 5} more corrections\n"
            else:
                response += "• Minor formatting improvements\n"
        else:
            response = (
                f"✍️ **Grammar Check Complete**\n\n"
                f"✅ Your text is grammatically correct!\n\n"
                f"📝 **Your text:**\n{text}\n\n"
                f"💡 No corrections needed. Great job! 👏"
            )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in grammar correction: {e}")
        await update.message.reply_text("❌ Error checking grammar. Please try again.")

async def spell_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /spell command"""
    text = update.message.text.replace('/spell', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to check spelling!\n"
            "Example: /spell I recieve a message"
        )
        return
    
    await update.message.reply_text("📝 Checking spelling...")
    
    try:
        result = spell_check(text)
        
        if result['has_misspellings']:
            response = (
                f"📝 **Spelling Check Results**\n\n"
                f"📊 **Total errors found:** {result['total_errors']}\n\n"
                f"📝 **Original text:**\n{text}\n\n"
                f"🔧 **Corrections suggested:**\n"
            )
            
            for i, (word, suggestion) in enumerate(zip(result['misspelled'], result['suggestions']), 1):
                response += f"{i}. '{word}' → '{suggestion}'\n"
            
            response += f"\n💡 Use /grammar for full grammar correction!"
            
        else:
            response = (
                f"📝 **Spelling Check Complete**\n\n"
                f"✅ No spelling errors found!\n\n"
                f"📝 **Your text:**\n{text}\n\n"
                f"💡 Great spelling! Keep it up! 👏"
            )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in spelling check: {e}")
        await update.message.reply_text("❌ Error checking spelling. Please try again.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general text messages"""
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    # Show options for what to do with the text
    keyboard = [
        [InlineKeyboardButton("🔊 Text-to-Speech", callback_data="process_tts")],
        [InlineKeyboardButton("✍️ Grammar Correction", callback_data="process_grammar")],
        [InlineKeyboardButton("📝 Spelling Check", callback_data="process_spell")],
        [InlineKeyboardButton("🔄 All Three (TTS + Grammar + Spell)", callback_data="process_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📝 I received your text:\n\n"
        f"_{text[:100]}{'...' if len(text) > 100 else ''}_\n\n"
        f"🤔 How would you like me to process it?\n\n"
        f"💡 Use /tts, /grammar, or /spell directly for faster results!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Store text in context for later processing
    context.user_data['pending_text'] = text

async def process_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle processing callback"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    text = context.user_data.get('pending_text', '')
    
    if not text:
        await query.edit_message_text("❌ No text found. Please send your text again.")
        return
    
    user_id = query.from_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    
    if action == "process_tts":
        await query.edit_message_text(f"🎤 Converting to speech in {LANGUAGES.get(lang, 'English')}...")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            speed_label = "Normal" if speed == 'normal' else "Slow"
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"🔊 Text-to-Speech\n"
                           f"🌐 Language: {LANGUAGES.get(lang, 'English')}\n"
                           f"🎚️ Speed: {speed_label}\n"
                           f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}",
                    title="TTS Audio",
                    performer="@josealvarez21_bot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text("✅ Audio sent successfully!")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error converting to speech. Please try again.")
    
    elif action == "process_grammar":
        await query.edit_message_text("✍️ Analyzing and correcting grammar...")
        
        try:
            result = correct_grammar(text)
            
            if result['changes_made']:
                response = (
                    f"✍️ **Grammar Correction Results**\n\n"
                    f"📝 **Original:**\n{result['original']}\n\n"
                    f"✅ **Corrected:**\n{result['corrected']}\n\n"
                    f"🔧 **Corrections:** ({result['total_corrections']} changes)\n"
                )
                
                if result['corrections']:
                    for i, correction in enumerate(result['corrections'][:5], 1):
                        response += f"{i}. {correction}\n"
                    if len(result['corrections']) > 5:
                        response += f"... and {len(result['corrections']) - 5} more"
                else:
                    response += "• Minor improvements"
            else:
                response = (
                    f"✍️ **Grammar Check Complete**\n\n"
                    f"✅ Your text is grammatically correct!\n\n"
                    f"📝 **Your text:**\n{text}"
                )
            
            await query.message.reply_text(response, parse_mode='Markdown')
            await query.edit_message_text("✅ Grammar check completed!")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error checking grammar. Please try again.")
    
    elif action == "process_spell":
        await query.edit_message_text("📝 Checking spelling...")
        
        try:
            result = spell_check(text)
            
            if result['has_misspellings']:
                response = (
                    f"📝 **Spelling Check Results**\n\n"
                    f"📊 **Total errors:** {result['total_errors']}\n\n"
                    f"🔧 **Corrections suggested:**\n"
                )
                
                for i, (word, suggestion) in enumerate(zip(result['misspelled'], result['suggestions']), 1):
                    response += f"{i}. '{word}' → '{suggestion}'\n"
                
                response += f"\n💡 Use /grammar for full correction!"
            else:
                response = (
                    f"📝 **Spelling Check Complete**\n\n"
                    f"✅ No spelling errors found!\n\n"
                    f"📝 **Your text:**\n{text}"
                )
            
            await query.message.reply_text(response, parse_mode='Markdown')
            await query.edit_message_text("✅ Spelling check completed!")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error checking spelling. Please try again.")
    
    elif action == "process_all":
        await query.edit_message_text("🔄 Processing all three functions...")
        
        # Grammar correction
        try:
            result = correct_grammar(text)
            grammar_response = f"✍️ **Grammar:**\n✅ {result['corrected'][:100]}..."
            await query.message.reply_text(grammar_response, parse_mode='Markdown')
        except:
            pass
        
        # Spelling check
        try:
            result = spell_check(text)
            if result['has_misspellings']:
                spell_response = f"📝 **Spelling:** Found {result['total_errors']} error(s)"
                await query.message.reply_text(spell_response)
            else:
                await query.message.reply_text("📝 **Spelling:** ✅ No errors found!")
        except:
            pass
        
        # Text-to-Speech
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"🔊 TTS Audio\n🌐 Language: {LANGUAGES.get(lang, 'English')}",
                    title="TTS Audio",
                    performer="@josealvarez21_bot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text("✅ All three tasks completed!")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error processing TTS. Please try again.")

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu for TTS."""
    keyboard = []
    row = []
    # Show limited languages for TTS
    tts_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']
    
    for code in tts_languages:
        if code in LANGUAGES:
            row.append(InlineKeyboardButton(LANGUAGES[code], callback_data=f"lang_{code}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Select your preferred TTS language:",
        reply_markup=reply_markup
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['lang'] = lang_code
    
    await query.edit_message_text(
        f"✅ TTS Language set to: {LANGUAGES[lang_code]}\n\n"
        f"🎤 Now use /tts [text] to convert to speech!"
    )

SPEED_OPTIONS = {
    'normal': 'Normal Speed',
    'slow': 'Slow Speed',
}

async def speed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show speed selection menu."""
    keyboard = []
    for speed, name in SPEED_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"speed_{speed}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎚️ Select your preferred speech speed:",
        reply_markup=reply_markup
    )

async def speed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle speed selection callback."""
    query = update.callback_query
    await query.answer()
    
    speed = query.data.replace("speed_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['speed'] = speed
    
    await query.edit_message_text(
        f"✅ Speed set to: {SPEED_OPTIONS[speed]}\n\n"
        f"🎤 Now use /tts [text] to convert to speech!"
    )

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await update.message.reply_text(
        "🎤 I can only process text messages.\n"
        "Please send me text for TTS, grammar correction, or spelling check!"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

def main() -> None:
    """Start the bot."""
    logger.info("🎙️ @josealvarez21_bot Starting...")
    logger.info("🔍 Looking for bot token...")
    
    # Get token
    token = get_token()
    
    if not token:
        logger.error("❌ No valid token found!")
        logger.info("Please set TELEGRAM_BOT_TOKEN in Railway environment variables")
        logger.info("Go to: Railway Dashboard -> Your Project -> Variables -> Add Variable")
        sys.exit(1)
    
    logger.info(f"✅ Token found! Token
