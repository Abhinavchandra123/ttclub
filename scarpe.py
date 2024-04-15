import asyncio
import random
import csv
import os
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import ChannelParticipant
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import UserPrivacyRestrictedError

# Initialize your Telegram bot
BOT_token = "6739685094:AAFat8NREszlG-HkEHxlPSErRtMIbja8h_0"

# Telegram API credentials
api_id = '22486594'
api_hash = '395cce66a097fb6b3c9934d7607d5a95'

# Path to CSV file
CSV_FILE = 'memberss.csv'

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

async def scrape_and_add():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Scrape members from the source channel
        source_channel = 'your_source_channel'
        destination_channel = 'your_destination_channel'
        participants = await client(GetParticipantsRequest(
            channel=source_channel,
            filter=ChannelParticipantsSearch(''),
            offset=0,
            limit=10,
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
            if added_count >= 5:
                break  # Stop if 40 members are already added
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

async def main():
    while True:
        await scrape_and_add()
        # Schedule the next execution 12 hours from now
        await asyncio.sleep(43200)  # 12 hours

# Start the event loop
if __name__ == '__main__':
    asyncio.run(main())
