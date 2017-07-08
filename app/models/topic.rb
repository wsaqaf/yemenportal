# == Schema Information
#
# Table name: topics
#
#  id         :integer          not null, primary key
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  topic_size :integer
#

class Topic < ApplicationRecord
  belongs_to :main_post, class_name: "Post", optional: true
  has_many :posts
end
