import axios from 'axios';
import winston from 'winston';

// Logger setup
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new winston.transports.File({ filename: 'logs/uniguru.log' })
  ]
});

class UniguruService {
  constructor(apiKey, baseUrl) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl || 'https://api.uniguru.com/v1';
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });
  }

  /**
   * Classify news content into categories
   * @param {string} title - News title
   * @param {string} content - News content
   * @returns {Promise<Object>} Classification result with category, subcategory, confidence
   */
  async classifyNews(title, content) {
    try {
      logger.info('Classifying news:', { title: title.substring(0, 50) });
      
      const response = await this.client.post('/classify', {
        title,
        content,
        returnTopN: 3
      });

      const result = response.data;
      return {
        category: result.primary_category,
        subcategory: result.subcategories ? result.subcategories[0] : null,
        confidence: result.confidence,
        alternatives: result.alternatives || [],
        timestamp: new Date()
      };
    } catch (error) {
      logger.error('Classification error:', error.message);
      throw new Error(`Uniguru classification failed: ${error.message}`);
    }
  }

  /**
   * Analyze sentiment of news content
   * @param {string} content - News content
   * @returns {Promise<Object>} Sentiment analysis with label, score, aspects
   */
  async analyzeSentiment(content) {
    try {
      logger.info('Analyzing sentiment');
      
      const response = await this.client.post('/sentiment', {
        text: content,
        includeAspects: true,
        returnConfidence: true
      });

      const result = response.data;
      return {
        label: result.overall_sentiment.toLowerCase(), // positive, negative, neutral
        score: result.sentiment_score, // -1 to 1
        confidence: result.confidence,
        aspects: result.aspect_sentiments?.map(asp => ({
          aspect: asp.aspect,
          sentiment: asp.sentiment.toLowerCase(),
          score: asp.score
        })) || [],
        timestamp: new Date()
      };
    } catch (error) {
      logger.error('Sentiment analysis error:', error.message);
      throw new Error(`Uniguru sentiment analysis failed: ${error.message}`);
    }
  }

  /**
   * Summarize news content at different levels
   * @param {string} title - News title
   * @param {string} content - News content
   * @returns {Promise<Object>} Summary result with short, medium summaries, key points, entities
   */
  async summarizeNews(title, content) {
    try {
      logger.info('Summarizing news');
      
      const response = await this.client.post('/summarize', {
        title,
        content,
        summaryLengths: ['short', 'medium'],  // 1-2 sentences, 1 paragraph
        includeKeyPoints: true,
        includeEntities: true,
        entityTypes: ['PERSON', 'ORG', 'LOCATION', 'EVENT', 'PRODUCT']
      });

      const result = response.data;
      return {
        short: result.short_summary,
        medium: result.medium_summary,
        keyPoints: result.key_points || [],
        entities: result.named_entities?.map(ent => ({
          type: ent.type,
          value: ent.text
        })) || [],
        timestamp: new Date()
      };
    } catch (error) {
      logger.error('Summarization error:', error.message);
      throw new Error(`Uniguru summarization failed: ${error.message}`);
    }
  }

  /**
   * Process complete news item (all three operations)
   * @param {string} title - News title
   * @param {string} content - News content
   * @returns {Promise<Object>} Combined classification, sentiment, summary
   */
  async processNewsComplete(title, content) {
    try {
      logger.info('Processing complete news enrichment');
      
      const startTime = Date.now();
      
      const [classification, sentiment, summary] = await Promise.all([
        this.classifyNews(title, content),
        this.analyzeSentiment(content),
        this.summarizeNews(title, content)
      ]);

      const duration = Date.now() - startTime;
      
      logger.info('News processing completed', {
        duration,
        classification: classification.category,
        sentiment: sentiment.label
      });

      return {
        classification,
        sentiment,
        summary,
        processingTime: duration,
        success: true
      };
    } catch (error) {
      logger.error('Complete news processing error:', error.message);
      throw error;
    }
  }

  /**
   * Batch process multiple news items
   * @param {Array} newsItems - Array of {title, content} objects
   * @returns {Promise<Array>} Array of processed results
   */
  async batchProcessNews(newsItems) {
    try {
      logger.info(`Batch processing ${newsItems.length} news items`);
      
      const results = await Promise.allSettled(
        newsItems.map(item => this.processNewsComplete(item.title, item.content))
      );

      return results.map((result, index) => ({
        itemIndex: index,
        status: result.status,
        data: result.status === 'fulfilled' ? result.value : null,
        error: result.status === 'rejected' ? result.reason.message : null
      }));
    } catch (error) {
      logger.error('Batch processing error:', error.message);
      throw error;
    }
  }

  /**
   * Verify health of Uniguru API
   * @returns {Promise<boolean>} API health status
   */
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      logger.error('Uniguru health check failed:', error.message);
      return false;
    }
  }
}

export default UniguruService;
