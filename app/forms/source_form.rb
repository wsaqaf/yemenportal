class SourceForm < Reform::Form
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

  validates :link, :name, presence: true
  validates :admin_email, email: true, if: :test
  validates :website, :link, url: true

  def test
    admin_email.present?
  end
end
