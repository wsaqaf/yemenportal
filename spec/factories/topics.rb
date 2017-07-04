# == Schema Information
#
# Table name: topics
#
#  id          :integer          not null, primary key
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  post_counts :integer
#

FactoryGirl.define do
  factory :topic do
  end
end
