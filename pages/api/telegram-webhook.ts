
'use server';
import { sendTelegramMessage } from '@/telegram_interactions/interactions';
import { TelegramMessageSchema } from '@/types/types';
import { NextApiRequest, NextApiResponse } from 'next';


export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === 'POST') {
        const update = req.body;

        const message = TelegramMessageSchema.safeParse(update.message);

        if (!message.success) {
            console.error('Invalid message format:', message.error);
            return res.status(400).send('Invalid message format');
        } else {
            console.log('Valid message received:', message.data);
        }

        // Process the message
        const result = await sendTelegramMessage({
            chat_id: message.data.chat.id,
            text: `Received message: ${message || 'No text'}`,
            image_url: '', // You can add an image URL if needed
        });

        if (result.isErr()) {
            console.error('Error sending message:', result.error);
            return res.status(500).send('Error sending message');
        }
        console.log('Message sent successfully');
        return res.status(200).send('Message processed successfully');
    }
}
