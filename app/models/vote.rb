# == Schema Information
#
# Table name: votes
#
#  id         :integer          not null, primary key
#  user_id    :integer          not null
#  value      :integer
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  post_id    :integer
#
# Indexes
#
#  index_votes_on_post_id  (post_id)
#  index_votes_on_user_id  (user_id)
#

class Vote < ApplicationRecord
  belongs_to :user
  belongs_to :post

  validates_uniqueness_of :post_id, scope: :user_id

  def self.create_upvote(params)
    create(params.merge(value: 1))
  end

  def self.create_downvote(params)
    create(params.merge(value: -1))
  end

  def self.voting_result_for(post)
    where(post: post).sum(:value)
  end

  def make_upvote
    update(value: 1)
  end

  def make_downvote
    update(value: -1)
  end
end
