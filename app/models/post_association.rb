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

class PostAssociation < ApplicationRecord
  belongs_to :main_post, class_name: "Post"
  belongs_to :dependent_post, class_name: "Post"
end
