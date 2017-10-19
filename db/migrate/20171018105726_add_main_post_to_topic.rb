class AddMainPostToTopic < ActiveRecord::Migration[5.0]
  class Topic < ApplicationRecord; end

  def up
    add_reference :topics, :main_post, foreign_key: { to_table: :posts }, on_delete: :cascade
    set_main_post_if_initial_post_exists
    remove_topics_without_main_post
    change_column_null :topics, :main_post_id, true
  end

  def down
    remove_reference :topics, :main_post
  end

  private

  def set_main_post_if_initial_post_exists
    execute <<-SQL
      UPDATE "topics" SET "main_post_id" = (
        SELECT "posts"."id"
        FROM "posts"
        WHERE "posts"."topic_id" ="topics"."id"
        ORDER BY "posts"."created_at", "posts"."id" ASC LIMIT(1)
      )
    SQL
  end

  def remove_topics_without_main_post
    Topic.where(main_post_id: nil).delete_all
  end
end
