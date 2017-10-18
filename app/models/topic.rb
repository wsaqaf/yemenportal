# == Schema Information
#
# Table name: topics
#
#  id         :integer          not null, primary key
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  topic_size :integer
#

class Topic < ApplicationRecord
  has_many :posts, dependent: :destroy

  scope :ordered_by_date, -> { order("topics.created_at DESC") }
  scope :ordered_by_size, -> { order("topic_size DESC") }

  def self.created_later_than(timestamp)
    where("topics.created_at > ?", timestamp)
  end

  def initial_post
    posts.min_by(&:created_at)
  end

  delegate :title, :source_name, :category_names, :description, :image_url, :link,
    :show_internally?, to: :initial_post

  def related_posts
    posts - [initial_post]
  end
end
