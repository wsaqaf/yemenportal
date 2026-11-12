from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('posts', '0012_post_shares_count_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddIndex(
                    model_name='post',
                    index=models.Index(
                        condition=models.Q(state='approved'),
                        fields=['source', '-published_at'],
                        name='idx_posts_approved_source_pub',
                    ),
                ),
                migrations.AddIndex(
                    model_name='post',
                    index=models.Index(
                        condition=models.Q(state='approved'),
                        fields=['topic', '-published_at'],
                        name='idx_posts_approved_topic_pub',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_approved_source_pub 
                    ON posts_post (source_id, published_at DESC) 
                    WHERE state = 'approved';

                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_approved_topic_pub 
                    ON posts_post (topic_id, published_at DESC) 
                    WHERE state = 'approved';
                    """,
                    reverse_sql="""
                    DROP INDEX CONCURRENTLY IF EXISTS idx_posts_approved_source_pub;
                    DROP INDEX CONCURRENTLY IF EXISTS idx_posts_approved_topic_pub;
                    """
                ),
            ],
        ),
    ]
