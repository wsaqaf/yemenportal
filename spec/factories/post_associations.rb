# == Schema Information
#
# Table name: post_associations
#
#  id                :integer          not null, primary key
#  main_post_id      :integer
#  dependent_post_id :integer
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#

FactoryGirl.define do
  factory :post_association do
    main_post nil
    dependent_post nil
  end
end
