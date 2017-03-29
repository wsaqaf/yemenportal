# == Schema Information
#
# Table name: identities
#
#  id         :integer          not null, primary key
#  user_id    :integer          not null
#  provider   :string
#  uid        :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_identities_on_user_id  (user_id)
#

FactoryGirl.define do
  factory :identity do
    association :user
    provider "twitter"
    sequence(:uid) { |n| "Uid_#{n}" }
  end
end
