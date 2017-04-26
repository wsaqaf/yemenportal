# == Schema Information
#
# Table name: users
#
#  id                     :integer          not null, primary key
#  email                  :string           default(""), not null
#  first_name             :string
#  last_name              :string
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#  role                   :enum             default("MEMBER"), not null
#  encrypted_password     :string           default(""), not null
#  reset_password_token   :string
#  reset_password_sent_at :datetime
#  remember_created_at    :datetime
#  sign_in_count          :integer          default("0"), not null
#  current_sign_in_at     :datetime
#  last_sign_in_at        :datetime
#  current_sign_in_ip     :inet
#  last_sign_in_ip        :inet
#  invitation_token       :string
#  invitation_created_at  :datetime
#  invitation_sent_at     :datetime
#  invitation_accepted_at :datetime
#  invitation_limit       :integer
#  invited_by_type        :string
#  invited_by_id          :integer
#  invitations_count      :integer          default("0")
#  confirmation_token     :string
#  confirmed_at           :datetime
#  confirmation_sent_at   :datetime
#  unconfirmed_email      :string
#
# Indexes
#
#  index_users_on_email                 (email) UNIQUE
#  index_users_on_invitation_token      (invitation_token) UNIQUE
#  index_users_on_invitations_count     (invitations_count)
#  index_users_on_invited_by_id         (invited_by_id)
#  index_users_on_reset_password_token  (reset_password_token) UNIQUE
#

class User < ApplicationRecord
  extend Enumerize

  # :confirmable, :lockable, :timeoutable and :omniauthable, :rememberable,
  devise :database_authenticatable, :registerable, :recoverable, :trackable, :confirmable, :invitable,
         :validatable, :omniauthable, omniauth_providers: [:facebook, :twitter]

  validates :email, :role, presence: true
  validates :email, uniqueness: true
  validates :email, email: true

  has_many :votes
  has_many :posts, through: :votes

  enumerize :role, in: %w(ADMIN MODERATOR MEMBER).map { |role| [role.downcase, role] }.to_h,
    i18n_scope: "user.roles"

  scope :moderators, -> { where(role: "MODERATOR") }

  def self.from_omniauth(auth)
    identity = Identity.find_by(provider: auth.provider, uid: auth.uid)

    if identity.nil?
      email = auth.info.email || "#{auth.info.nickname}_#{auth.provider}@yemenportal.com"
      identity = Identity.create(uid: auth.uid, provider: auth.provider, user: User.user_for_auth(email))
    end

    identity.user
  end

  def self.user_for_auth(email)
    user = User.find_by(email: email) || User.new(email: email, password: Devise.friendly_token[0, 20])
    unless user.persisted?
      user.skip_confirmation!
      user.save
    end
    user
  end
end
