class ApplySourceCategoryToPosts < ActiveRecord::Migration[5.0]
  def up
    execute <<-SQL
      INSERT INTO "post_categories" (post_id, category_id, created_at, updated_at)
        SELECT "posts"."id", "sources"."category_id", now(), now()
        FROM "posts"
        INNER JOIN "sources"
          ON "posts"."source_id" = "sources"."id"
            AND "sources"."category_id" IS NOT NULL
        WHERE NOT EXISTS (
          SELECT * FROM post_categories
          WHERE "post_categories"."post_id" = "posts"."id"
            AND "post_categories"."category_id" = "sources"."category_id"
        );
    SQL
  end

  def down
    false
  end
end
