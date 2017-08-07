# == Schema Information
#
# Table name: topics
#
#  id            :integer          not null, primary key
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#  topic_size    :integer
#  voting_result :integer          default("0")
#
# Indexes
#
#  index_topics_on_voting_result  (voting_result)
#

class Topic < ApplicationRecord
  has_many :posts
  has_many :votes, dependent: :destroy

  scope :ordered_by_date, -> { order("updated_at DESC") }

  def initial_post
    posts.latest
  end

  delegate :title, :source_name, :category_names, :description, :image_url, to: :initial_post

  def related_posts
    []
  end

  def update_voting_result(new_value)
    update(voting_result: new_value)
  end
end
