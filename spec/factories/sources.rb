# == Schema Information
#
# Table name: sources
#
#  id         :integer          not null, primary key
#  link       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

FactoryGirl.define do
  factory :source do
    sequence(:link) { |n| "www.source_#{n}@gar.com" }
  end
end
