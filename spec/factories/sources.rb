# == Schema Information
#
# Table name: sources
#
#  id             :integer          not null, primary key
#  link           :string           not null
#  created_at     :datetime         not null
#  updated_at     :datetime         not null
#  category_id    :integer
#  state          :string           default("valid")
#  whitelisted    :boolean          default("false")
#  name           :string           default(""), not null
#  website        :string
#  brief_info     :string
#  admin_email    :string
#  admin_name     :string
#  note           :string
#  approve_state  :string
#  suggested_time :datetime
#  user_id        :integer
#
# Indexes
#
#  index_sources_on_category_id  (category_id)
#  index_sources_on_user_id      (user_id)
#

FactoryGirl.define do
  factory :source do
    sequence(:link) { |n| "www.source_#{n}@gar.com" }
    association :category
    whitelisted false
  end
end
