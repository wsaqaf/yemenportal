class SourceForm < Reform::Form
  extend Enumerize
  WEBSITE_REGEXP = %r((http|https){1}\:\/\/[^\/]+)

  property :name
  property :admin_email
  property :admin_name
  property :category_id
  property :link
  property :website, populator: ->(doc:, **) do
    link = doc[:link]
    website = doc[:website]
    self.website = website.present? ? website : (link && link.match(WEBSITE_REGEXP).to_s)
  end
  property :brief_info
  property :note
  property :whitelisted
  property :category_id
  property :state
  property :approve_state
  property :source_type
  property :user
  property :iframe_flag

  validates :link, :name, presence: true
  validates :admin_email, email: true, if: "admin_email.present?"
  validates :website, :link, url: true

  enumerize :approve_state, in: [:approved, :suggested], default: :suggested
  enumerize :source_type, in: [:rss, :facebook], default: :rss
end
