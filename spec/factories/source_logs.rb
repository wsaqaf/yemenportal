# == Schema Information
#
# Table name: source_logs
#
#  id          :integer          not null, primary key
#  state       :string
#  source_id   :integer          not null
#  posts_count :integer          default("0")
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_source_logs_on_source_id  (source_id)
#

FactoryGirl.define do
  factory :source_log do
    state "MyString"
    posts_count 1
    association :source
  end
end
