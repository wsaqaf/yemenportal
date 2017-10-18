class AddMainPostToTopic < ActiveRecord::Migration[5.0]
  class Topic < ApplicationRecord
    has_many :posts, dependent: :destroy

    def initial_post
      posts.min_by(&:created_at)
    end
  end

  def up
    add_reference :topics, :main_post, foreign_key: { to_table: :posts }, on_delete: :cascade
    Topic.find_each { |topic| TopicMainPostMigration.new(topic).up }
    change_column_null :topics, :main_post_id, true
  end

  def down
    remove_reference :topics, :main_post
  end

  class TopicMainPostMigration
    def initialize(topic)
      @topic = topic
      @initial_post_id = topic.initial_post&.id
    end

    def up
      if @initial_post_id.present?
        @topic.update(main_post_id: @initial_post_id)
      else
        @topic.destroy
      end
    end
  end
end
