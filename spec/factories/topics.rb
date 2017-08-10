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

FactoryGirl.define do
  factory :topic do
  end
end
