import { NextResponse } from 'next/server';
import clientPromise from '@/lib/mongodb';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const client = await clientPromise;
    const db = client.db('global_pulse');
    const collection = db.collection('global_sentiment');

    // Fetch the latest 500 documents sorted by _id descending (newest first)
    const documents = await collection
      .find({})
      .sort({ _id: -1 })
      .limit(500)
      .toArray();

    return NextResponse.json({ success: true, data: documents });
  } catch (error) {
    console.error('Failed to fetch sentiment data:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch data from database' },
      { status: 500 }
    );
  }
}
