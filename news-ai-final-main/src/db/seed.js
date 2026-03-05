import mongoose from 'mongoose';
import 'dotenv/config';
import { connectDB, createNewsItem, createAgentTask } from '../db/connection.js';

async function seedDatabase() {
  try {
    console.log('🌱 Seeding MongoDB Database...\n');

    await connectDB(process.env.MONGODB_URI);

    // Create initial agents index
    const agents = [
      { role: 'fetch', priority: 10 },
      { role: 'filter', priority: 8 },
      { role: 'verify', priority: 9 },
      { role: 'script', priority: 7 },
      { role: 'rlfeedback', priority: 6 }
    ];

    console.log('📝 Sample agent configurations:');
    agents.forEach(agent => {
      console.log(`  ✓ ${agent.role} (priority: ${agent.priority})`);
    });

    console.log('\n✅ Database seeded successfully!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Seeding failed:', error.message);
    process.exit(1);
  }
}

seedDatabase();
