class AddReviewRatingToPosts < ActiveRecord::Migration[5.0]
  class Flags < ApplicationRecord; end

  def change
    add_column :posts, :review_rating, :integer, null: false, default: 0
    add_column :flags, :rate, :integer, null: false, default: 0
    add_rate_to_existing_flags
    count_review_rating_for_existing_posts
  end

  def add_rate_to_existing_flags
    flags.each do |_, flag_attributes|
      Flag
        .where(name: flag_attributes[:name])
        .update_all(rate: flag_attributes[:rate])
    end
  end

  def count_review_rating_for_existing_posts
    execute <<-SQL
      CREATE TEMP TABLE "posts_ratings" AS
        SELECT "posts"."id" AS "post_id", SUM("flags"."rate") AS "rate"
        FROM "flags"
        INNER JOIN "reviews" ON "reviews"."flag_id" = "flags"."id"
          INNER JOIN "posts" ON "posts"."id" = "reviews"."post_id"
        GROUP BY "posts"."id";

      UPDATE "posts" SET "review_rating" = "posts_ratings"."rate"
      FROM "posts_ratings"
      WHERE "posts_ratings"."post_id" = "posts"."id";
    SQL
  end

  def flags
    {
      passed: { name: "تمت المراجعة", rate: 1 },
      copied: { name: "منقول", rate: -1 },
      deceitful: { name: "مضلل", rate: -1 },
      missing_reference: { name: "بلا مرجع", rate: -1 },
      other: { name: "ملاحظة أخرى", rate: -1 }
    }
  end
end
