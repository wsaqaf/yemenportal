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

class User < ApplicationRecord
  extend Enumerize
  validates :email, :role, presence: true
  validates :email, uniqueness: true

  enumerize :role, in: %w(ADMIN MODERATOR MEMBER).map { |role| [role.downcase, role] }.to_h,
    i18n_scope: "user.roles"

  scope :moderators, -> { where(role: "MODERATOR") }
end
