# == Schema Information
#
# Table name: flags
#
#  id      :integer          not null, primary key
#  name    :string
#  color   :string
#  resolve :boolean          default("false"), not null
#  rate    :integer          default("0"), not null
#

class Flag < ApplicationRecord
  has_many :reviews, dependent: :destroy
  scope :reviewed_flags, ->(post) { include_number_of_reviews_for_post(post).having("COUNT(reviews.*) > 0") }

  def self.include_number_of_reviews_for_post(post)
    joins("LEFT JOIN reviews ON reviews.flag_id = flags.id AND reviews.post_id = #{post.id}")
      .group(:id).select("flags.*, COUNT(reviews.*) AS number_of_reviews_for_post")
  end

  def number_of_reviews_for_post
    attributes["number_of_reviews_for_post"] || 0
  end
end
