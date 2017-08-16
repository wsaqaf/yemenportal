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
  has_many :posts, dependent: :destroy
  has_many :votes, dependent: :destroy
  has_many :reviews, dependent: :destroy
  has_many :review_comments, -> { ordered_by_date }, dependent: :destroy

  scope :ordered_by_date, -> { order("topics.created_at DESC") }
  scope :ordered_by_voting_result, -> { order("voting_result DESC") }
  scope :ordered_by_size, -> { order("topic_size DESC") }

  def self.include_voted_by_user(user)
    joins("LEFT JOIN votes ON votes.topic_id = topics.id AND votes.user_id = #{user.id}")
      .group(:id).select("topics.*,
        (COUNT(votes.*) > 0 AND SUM(votes.value) > 0) AS upvoted_by_user,
        (COUNT(votes.*) > 0 AND SUM(votes.value) < 0) AS downvoted_by_user")
  end

  def self.created_later_than(timestamp)
    where("topics.created_at > ?", timestamp)
  end

  def self.include_review_comments
    includes(review_comments: [:author])
  end

  def upvoted_by_user?
    attributes["upvoted_by_user"] || false
  end

  def downvoted_by_user?
    attributes["downvoted_by_user"] || false
  end

  def initial_post
    posts.min_by(&:created_at)
  end

  delegate :title, :source_name, :category_names, :description, :image_url, :link,
    :show_internally?, to: :initial_post

  def related_posts
    posts - [initial_post]
  end

  def update_voting_result(new_value)
    update(voting_result: new_value)
  end
end
