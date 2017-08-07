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

  scope :ordered_by_date, -> { order("created_at DESC") }

  def self.include_voted_by_user(user)
    joins("LEFT JOIN votes ON votes.topic_id = topics.id AND votes.user_id = #{user.id}")
      .group(:id).select("topics.*,
        (COUNT(votes.*) > 0 AND SUM(votes.value) > 0) AS upvoted_by_user,
        (COUNT(votes.*) > 0 AND SUM(votes.value) < 0) AS downvoted_by_user")
  end

  def upvoted_by_user?
    attributes["upvoted_by_user"] || false
  end

  def downvoted_by_user?
    attributes["downvoted_by_user"] || false
  end

  def initial_post
    posts.min_by { |post| post.created_at }
  end

  delegate :title, :source_name, :category_names, :description, :image_url, to: :initial_post

  def related_posts
    posts - [initial_post]
  end

  def update_voting_result(new_value)
    update(voting_result: new_value)
  end
end
