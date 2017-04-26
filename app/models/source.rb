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

class Source < ApplicationRecord
  extend Enumerize
  has_many :posts
  has_many :source_logs
  belongs_to :category, optional: true

  validates :link, :name, presence: true
  validates :admin_email, email: true, if: :test
  validates :website, :link, url: true
  enumerize :state, in: [:valid, :incorrect_path, :incorrect_stucture, :not_full_info], default: :valid
  enumerize :approve_state, in: [:approved, :suggested], default: :suggested

  def test
    admin_email.present?
  end
end
