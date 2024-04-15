import asyncio
import random
import csv
import os
from datetime import datetime, timedelta
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import ChannelParticipant
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import UserPrivacyRestrictedError
import telebot

# Initialize your Telegram bot
BOT_token = "6739685094:AAFat8NREszlG-HkEHxlPSErRtMIbja8h_0"
bot = telebot.TeleBot(BOT_token)

# Telegram API credentials
api_id = '22486594'
api_hash = '395cce66a097fb6b3c9934d7607d5a95'

# Path to CSV file
CSV_FILE = 'members.csv'

# Function to write members to CSV
def write_to_csv(member_ids):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(member_ids)

# Function to read members from CSV
def read_from_csv():
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            return [row[0] for row in reader]
    return []

# Function to send a notification message using Telegram bot
def send_notification_message(message_text):
    bot.send_message(chat_id='1193361700', text=message_text)

# Function to scrape members from source channel and add to destination channel
async def scrape_and_add(source_channel, destination_channel):
    async with TelegramClient('session_name', api_id, api_hash, timeout=50000) as client:
        participants = await client(GetParticipantsRequest(
            channel=source_channel,
            filter=ChannelParticipantsSearch(''),
            offset=0,
            limit=1000,
            hash=0
        ))
        member_ids = []
        for participant in participants.participants:
            if isinstance(participant, ChannelParticipant):
                member_ids.append(participant.user_id)

        # Shuffle member IDs
        random.shuffle(member_ids)

        # Add scraped members to the destination channel
        added_count = 0
        for member_id in member_ids:
            if added_count >= 2:
                break
            if member_id not in read_from_csv():
                try:
                    await client(InviteToChannelRequest(
                        channel=destination_channel,
                        users=[member_id]
                    ))
                    added_count += 1
                    write_to_csv([member_id])  # Write to CSV if successfully added
                    print(f"Added user with ID {member_id} to the destination channel.")
                except UserPrivacyRestrictedError:
                    print(f"Skipped user with ID {member_id} due to privacy settings.")
                    continue
                except Exception as e:
                    print(f"Failed to add user with ID {member_id} to the destination channel: {str(e)}")

                    # Send notification message
                    send_notification_message(f"Failed to add user with ID {member_id} to the destination channel: {str(e)}")

# Schedule the next execution after 24 hours
async def schedule_next_execution(source_channel, destination_channel):
    while True:
        # Run the scrape_and_add function
        await scrape_and_add(source_channel, destination_channel)
        # Sleep for 24 hours
        await asyncio.sleep(2000)
        next_schedule = datetime.now() + timedelta(minutes=30)
        send_notification_message("next execution will be after 30 minutes")

# Start the event loop
async def main():
    # Replace 'your_source_channel_name' and 'your_destination_channel_name' with your actual channel names
    source_channel = '@HelpSeminar2'
    destination_channel = '@salmanfilk'
    await schedule_next_execution(source_channel, destination_channel)

asyncio.run(main())
