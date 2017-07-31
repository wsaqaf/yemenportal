# == Schema Information
#
# Table name: sources
#
#  id            :integer          not null, primary key
#  link          :string           not null
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#  category_id   :integer
#  state         :string           default("valid")
#  whitelisted   :boolean          default("false")
#  name          :string           default(""), not null
#  website       :string
#  brief_info    :string
#  admin_email   :string
#  admin_name    :string
#  note          :string
#  source_type   :string
#  approve_state :string           default("suggested")
#  user_id       :integer
#  iframe_flag   :boolean          default("true")
#  logo_url      :string
#
# Indexes
#
#  index_sources_on_category_id  (category_id)
#  index_sources_on_user_id      (user_id)
#

class Source < ApplicationRecord
  extend Enumerize
  FACEBOOK_REGEXP = %r{(?<=www\.facebook\.com\/)[^\/]+}

  has_many :posts
  has_many :source_logs
  belongs_to :category, optional: true
  belongs_to :user, optional: true

  validates :link, :name, presence: true
  validates :admin_email, email: true, if: "admin_email.present?"
  validates :website, :link, url: true
  validates :link, uniqueness: true

  enumerize :state, in: [:valid, :incorrect_path, :incorrect_stucture, :not_full_info, :other], default: :valid
  enumerize :approve_state, in: [:approved, :suggested, :disabled], default: :suggested
  enumerize :source_type, in: [:rss, :facebook], default: :rss

  scope :suggested, -> { where(approve_state: [:suggested, nil]) }
  scope :approved, -> { where(approve_state: :approved) }
  scope :by_state, ->(state) { where(approve_state: state) }

  def facebook_page
    link.match(FACEBOOK_REGEXP).to_s if source_type.facebook?
  end
end
