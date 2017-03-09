# == Schema Information
#
# Table name: users
#
#  id         :integer          not null, primary key
#  email      :string
#  first_name :string
#  last_name  :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  role       :enum             default("MEMBER"), not null
#

FactoryGirl.define do
  factory :user do
    sequence(:email) { |n| "yemenpotral_#{n}@yem.ar" }
    sequence(:first_name) { |n| "first_name_#{n}" }
    sequence(:last_name) { |n| "last_name_#{n}" }
  end
end
