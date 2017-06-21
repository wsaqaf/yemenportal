# == Schema Information
#
# Table name: stop_words
#
#  id         :integer          not null, primary key
#  name       :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

FactoryGirl.define do
  factory :stop_word do
    name "MyString"
  end
end
