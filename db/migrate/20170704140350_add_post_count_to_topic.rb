class AddPostCountToTopic < ActiveRecord::Migration[5.0]
  class Post < ApplicationRecord
    belongs_to :topic, optional: true, counter_cache: :topic_size
  end

  class Topic < ApplicationRecord
    has_many :posts
  end

  def up
    add_column :topics, :topic_size, :integer

    Topic.find_each { |topic| Topic.reset_counters(topic.id, :posts) }
  end

  def down
    remove_column :topics, :topic_size
  end
end
