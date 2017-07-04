class AddPostCountToTopic < ActiveRecord::Migration[5.0]
  class Post < ApplicationRecord
    belongs_to :topic, optional: true, counter_cache: :post_counts
  end

  class Topic < ApplicationRecord
    has_many :posts
  end

  def up
    add_column :topics, :post_counts, :integer

    Post.find_each { |post| Post.reset_counters(post.id, :comments) }
  end

  def down
    remove_column :topics, :post_counts
  end
end
