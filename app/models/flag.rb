# == Schema Information
#
# Table name: flags
#
#  id      :integer          not null, primary key
#  name    :string
#  color   :string
#  resolve :boolean          default("false"), not null
#

class Flag < ApplicationRecord
  has_many :reviews, dependent: :destroy

  def self.include_number_of_reviews_for_topic(topic)
    joins("LEFT JOIN reviews ON reviews.flag_id = flags.id AND reviews.topic_id = #{topic.id}")
      .group(:id).select("flags.*, COUNT(reviews.*) AS number_of_reviews_for_topic")
  end

  def self.include_topic_reviewed_by_user(topic, user)
    joins("LEFT JOIN reviews ON reviews.flag_id = flags.id
      AND reviews.topic_id = #{topic.id} AND reviews.moderator_id = #{user.id}")
      .group(:id).select("flags.*, (COUNT(reviews.*) > 0) AS topic_reviewed_by_user")
  end

  def number_of_reviews_for_topic
    attributes["number_of_reviews_for_topic"] || 0
  end

  def topic_reviewed_by_user?
    attributes["topic_reviewed_by_user"] || false
  end
end
