# == Schema Information
#
# Table name: sources
#
#  id          :integer          not null, primary key
#  link        :string           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  category_id :integer
#  state       :string           default("valid")
#  whitelisted :boolean          default("false")
#
# Indexes
#
#  index_sources_on_category_id  (category_id)
#

FactoryGirl.define do
  factory :source do
    sequence(:link) { |n| "www.source_#{n}@gar.com" }
    association :category
  end
end
