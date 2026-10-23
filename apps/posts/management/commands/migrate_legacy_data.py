import os
import sys
import time
import warnings
from django.core.management.base import BaseCommand
from django.db import connections, transaction, models
from apps.users.models import User
from apps.sources.models import Source, SourceLog
from apps.posts.models import Post, Category, Topic, Vote, PostView
from apps.moderation.models import Flag, Review, ReviewComment

warnings.filterwarnings('ignore', category=RuntimeWarning, module='django.db.models.fields')


class Command(BaseCommand):
    help = 'Migrates data from legacy Yemen Portal database using keyset pagination'

    def add_arguments(self, parser):
        parser.add_argument(
            '--step',
            type=str,
            default='all',
            choices=['all', 'categories', 'users', 'sources', 'posts', 'post_categories', 'votes', 'metrics', 'reset_sequences'],
            help='Specify which migration step to run (default: all)'
        )
        parser.add_argument(
            '--start-id',
            type=int,
            default=None,
            help='Starting post ID for keyset pagination (descending: starts from this ID down)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=25000,
            help='Batch size for database reads and bulk insertions (default: 25000)'
        )

    def handle(self, *args, **options):
        step = options['step']
        start_id = options['start_id']
        batch_size = options['batch_size']

        self.stdout.write(self.style.NOTICE(f"=== Starting migration process (step: {step}) ==="))

        if step in ('all', 'categories'):
            self.migrate_categories()

        if step in ('all', 'users'):
            self.migrate_users()

        if step in ('all', 'sources'):
            self.migrate_sources()

        if step in ('all', 'posts'):
            self.migrate_posts(start_id=start_id, batch_size=5000)

        if step in ('all', 'post_categories'):
            self.migrate_post_categories(batch_size=batch_size)

        if step in ('all', 'votes'):
            self.migrate_votes()

        if step in ('all', 'metrics'):
            self.sync_post_metrics(batch_size=5000)

        if step in ('all', 'reset_sequences'):
            self.reset_db_sequences()

        self.stdout.write(self.style.SUCCESS("=== Migration execution completed! ==="))

    def migrate_categories(self):
        self.stdout.write("Migrating categories...")
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT id, name, created_at, updated_at FROM categories")
            rows = cursor.fetchall()
            
            categories = [
                Category(id=r[0], name=r[1], created_at=r[2], updated_at=r[3])
                for r in rows
            ]
            Category.objects.bulk_create(categories, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(categories)} categories."))

    def migrate_users(self):
        self.stdout.write("Migrating users...")
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT id, email, encrypted_password, first_name, last_name, role, created_at, updated_at FROM users")
            rows = cursor.fetchall()
            
            users = [
                User(
                    id=r[0],
                    email=r[1],
                    password=r[2],
                    first_name=r[3] or '',
                    last_name=r[4] or '',
                    role=r[5],
                    created_at=r[6],
                    updated_at=r[7]
                )
                for r in rows
            ]
            User.objects.bulk_create(users, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(users)} users."))

    def migrate_sources(self):
        self.stdout.write("Migrating sources...")
        junk_names = {'Ruby', 'Test', 'Test feed', 'Text Feed', 'Text feed'}
        
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT id, name, link, website, brief_info, state, approve_state, user_id, iframe_flag, logo_url, created_at, updated_at FROM sources")
            rows = cursor.fetchall()
            
            created_count = 0
            for row in rows:
                name = (row[1] or '').strip()
                if not name or name in junk_names:
                    continue
                
                existing = Source.objects.filter(models.Q(name=name) | models.Q(link=row[2])).first()
                if existing:
                    continue
                
                Source.objects.create(
                    id=row[0],
                    name=name,
                    link=row[2],
                    website=row[3],
                    brief_info=row[4],
                    state=row[5],
                    approve_state=row[6],
                    user_id=row[7],
                    iframe_flag=row[8],
                    logo_url=row[9],
                    created_at=row[10],
                    updated_at=row[11]
                )
                created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Migrated {created_count} new sources."))

    def build_source_map(self):
        self.stdout.write("Building legacy to Django source mapping...")
        django_sources = {s.id: s.name.strip() for s in Source.objects.all()}
        django_name_to_id = {s.name.strip(): s.id for s in Source.objects.all()}

        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT id, name FROM sources")
            legacy_sources = {r[0]: (r[1] or '').strip() for r in cursor.fetchall()}

        source_map = {}
        for leg_id, leg_name in legacy_sources.items():
            if leg_id in django_sources:
                source_map[leg_id] = leg_id
            elif leg_name in django_name_to_id:
                source_map[leg_id] = django_name_to_id[leg_name]

        self.stdout.write(self.style.SUCCESS(f"Mapped {len(source_map)} legacy sources to active Django sources."))
        return source_map

    def migrate_posts(self, start_id=None, batch_size=5000):
        source_map = self.build_source_map()
        
        if start_id is None:
            with connections['legacy'].cursor() as cursor:
                cursor.execute("SELECT MAX(id) FROM posts")
                start_id = cursor.fetchone()[0]
                if start_id is None:
                    self.stdout.write(self.style.WARNING("No posts found in legacy database."))
                    return
            current_id = start_id + 1
        else:
            current_id = start_id + 1

        self.stdout.write(f"Starting post migration with keyset pagination from ID < {current_id} (batch size: {batch_size})...")

        total_processed = 0
        total_created = 0
        start_time = time.time()

        while True:
            batch_start = time.time()
            with connections['legacy'].cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, description, link, 
                           CASE 
                               WHEN published_at < '1901-01-01' THEN '1901-01-01 00:00:00+00'::timestamptz 
                               ELSE COALESCE(published_at, created_at, NOW()) AT TIME ZONE 'UTC' 
                           END AS pub_date, 
                           state, image_url, source_id, topic_id, voting_result, post_views_count, review_rating, 
                           COALESCE(created_at, NOW()) AT TIME ZONE 'UTC', 
                           COALESCE(updated_at, created_at, NOW()) AT TIME ZONE 'UTC' 
                    FROM posts 
                    WHERE id < %s AND title IS NOT NULL AND title != ''
                    ORDER BY id DESC 
                    LIMIT %s
                """, [current_id, batch_size])
                rows = cursor.fetchall()

            if not rows:
                self.stdout.write(self.style.SUCCESS("No more posts to fetch. Keyset pagination reached the end."))
                break

            current_id = rows[-1][0]

            posts_to_create = []
            for row in rows:
                target_source_id = source_map.get(row[7])
                if not target_source_id:
                    continue

                posts_to_create.append(Post(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    link=row[3],
                    published_at=row[4],
                    state='approved',
                    image_url=row[6],
                    stemmed_text='',
                    source_id=target_source_id,
                    topic_id=None,
                    voting_result=row[9] or 0,
                    post_views_count=row[10] or 0,
                    review_rating=row[11] or 0,
                    created_at=row[12],
                    updated_at=row[13]
                ))

            created_batch_count = 0
            if posts_to_create:
                with transaction.atomic():
                    created_objs = Post.objects.bulk_create(posts_to_create, ignore_conflicts=True)
                    created_batch_count = len(created_objs)

            total_processed += len(rows)
            total_created += created_batch_count
            elapsed = time.time() - start_time
            batch_dur = time.time() - batch_start
            rate = total_processed / elapsed if elapsed > 0 else 0

            self.stdout.write(
                f"ID: {current_id:>8} | Processed: {total_processed:>8} (Created: {total_created:>8}) | "
                f"Rate: {rate:>6.0f}/s | Batch: {batch_dur:.2f}s"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Finished posts migration: {total_processed} processed, {total_created} inserted in {elapsed:.1f}s."
        ))

    def migrate_post_categories(self, batch_size=25000):
        self.stdout.write("Loading valid Post and Category IDs from Django DB into memory...")
        t_load = time.time()
        valid_post_ids = set(Post.objects.values_list('id', flat=True))
        valid_category_ids = set(Category.objects.values_list('id', flat=True))
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(valid_post_ids):,} posts and {len(valid_category_ids)} categories in {time.time()-t_load:.1f}s."
        ))

        self.stdout.write(f"Migrating post categories using keyset pagination (batch size: {batch_size})...")
        current_id = 0
        total_processed = 0
        total_inserted = 0
        total_skipped = 0
        start_time = time.time()

        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT MIN(id) FROM post_categories")
            min_id = cursor.fetchone()[0]
            if min_id is not None:
                current_id = min_id - 1

        while True:
            batch_start = time.time()
            with connections['legacy'].cursor() as cursor:
                cursor.execute("""
                    SELECT id, post_id, category_id 
                    FROM post_categories 
                    WHERE id > %s 
                    ORDER BY id ASC 
                    LIMIT %s
                """, [current_id, batch_size])
                rows = cursor.fetchall()

            if not rows:
                break

            current_id = rows[-1][0]
            total_processed += len(rows)

            # Filter valid foreign keys and deduplicate within batch
            valid_pairs = set()
            batch_skipped = 0
            for r in rows:
                p_id, c_id = r[1], r[2]
                if p_id in valid_post_ids and c_id in valid_category_ids:
                    valid_pairs.add((p_id, c_id))
                else:
                    batch_skipped += 1

            total_skipped += batch_skipped

            if valid_pairs:
                with connections['default'].cursor() as django_cursor:
                    values_str = ",".join([f"({p}, {c})" for p, c in valid_pairs])
                    django_cursor.execute(f"""
                        INSERT INTO posts_post_categories (post_id, category_id) 
                        VALUES {values_str} 
                        ON CONFLICT DO NOTHING
                    """)
                    total_inserted += len(valid_pairs)

            elapsed = time.time() - start_time
            rate = total_processed / elapsed if elapsed > 0 else 0
            batch_dur = time.time() - batch_start

            self.stdout.write(
                f"Category Link ID: {current_id:>8} | Processed: {total_processed:>8} | "
                f"Valid: {total_inserted:>8} | Skipped: {total_skipped:>6} | "
                f"Rate: {rate:>6.0f}/s | Batch: {batch_dur:.2f}s"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Finished post_categories migration: {total_processed} processed, "
            f"{total_inserted} inserted, {total_skipped} skipped in {elapsed:.1f}s."
        ))

    def migrate_votes(self):
        self.stdout.write("Migrating votes...")
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT id, user_id, post_id, value, created_at, updated_at FROM votes")
            rows = cursor.fetchall()

        existing_users = set(User.objects.values_list('id', flat=True))
        existing_posts = set(Post.objects.values_list('id', flat=True))

        votes = []
        skipped = 0
        for row in rows:
            if row[1] in existing_users and row[2] in existing_posts:
                votes.append(Vote(
                    id=row[0],
                    user_id=row[1],
                    post_id=row[2],
                    value=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                ))
            else:
                skipped += 1

        if votes:
            Vote.objects.bulk_create(votes, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Migrated {len(votes)} votes ({skipped} skipped)."))

    def sync_post_metrics(self, batch_size=5000):
        self.stdout.write("Syncing post metrics with keyset pagination...")
        current_id = 0
        total_processed = 0

        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT MIN(id) FROM posts")
            min_id = cursor.fetchone()[0]
            if min_id is not None:
                current_id = min_id - 1

        while True:
            with connections['legacy'].cursor() as cursor:
                cursor.execute("""
                    SELECT id, voting_result, post_views_count 
                    FROM posts 
                    WHERE id > %s 
                    ORDER BY id ASC 
                    LIMIT %s
                """, [current_id, batch_size])
                rows = cursor.fetchall()

            if not rows:
                break

            current_id = rows[-1][0]
            total_processed += len(rows)

            updates = [
                Post(id=r[0], voting_result=r[1] or 0, post_views_count=r[2] or 0)
                for r in rows
            ]
            if updates:
                Post.objects.bulk_update(updates, ['voting_result', 'post_views_count'])

            if total_processed % 50000 < batch_size:
                self.stdout.write(f"Synced metrics for {total_processed} posts...")

        self.stdout.write(self.style.SUCCESS(f"Post metrics sync completed: {total_processed} processed."))

    def reset_db_sequences(self):
        self.stdout.write("Resetting PostgreSQL sequences to highest IDs...")
        tables = [
            ('posts_post', 'id'),
            ('posts_category', 'id'),
            ('posts_post_categories', 'id'),
            ('sources_source', 'id'),
            ('users_user', 'id'),
            ('posts_vote', 'id'),
        ]
        with connections['default'].cursor() as cursor:
            for table, pk_col in tables:
                cursor.execute(f"""
                    SELECT pg_get_serial_sequence('{table}', '{pk_col}');
                """)
                seq_res = cursor.fetchone()
                if seq_res and seq_res[0]:
                    seq_name = seq_res[0]
                    cursor.execute(f"""
                        SELECT setval('{seq_name}', COALESCE((SELECT MAX({pk_col}) FROM {table}), 1));
                    """)
                    self.stdout.write(f"Reset sequence {seq_name} for table {table}.")
                else:
                    self.stdout.write(self.style.WARNING(f"No serial sequence found for {table}.{pk_col}"))
        self.stdout.write(self.style.SUCCESS("All database sequences successfully synchronized!"))
