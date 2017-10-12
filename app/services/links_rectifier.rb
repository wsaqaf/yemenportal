class LinksRectifier
  def initialize(base_page_url, page_content)
    @url_rectifier = UrlRectifier.new(base_page_url)
    @content = Nokogiri::HTML(page_content)
  end

  def content_with_rectified_links
    rectify_page_links
    @content.inner_html
  end

  private

  def rectify_page_links
    @content.search(*tags_with_url_attributes).each do |tag|
      tag_attributes(tag.name).each do |attr|
        tag[attr] = @url_rectifier.rectify(tag[attr]) if tag[attr].present?
      end
    end
  end

  def config
    AttributesConfig.instance
  end

  delegate :tags_with_url_attributes, :tag_attributes, to: :config
end
