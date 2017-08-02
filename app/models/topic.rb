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
  has_many :posts

  scope :ordered_by_date, -> { order("created_at DESC") }

  def initial_post
    posts.latest
  end

  delegate :title, :source_name, :category_names, :description, :image_url, to: :initial_post

  def number_of_votes
    0
  end

  def related_posts
    []
  end
end
