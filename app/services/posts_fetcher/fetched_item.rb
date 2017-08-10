class PostsFetcher::FetchedItem
  def initialize(params)
    @params = params
  end

  def link
    params[:link]
  end

  def title
    params[:title]
  end

  def description
    sanitized_description
  end

  def published_at
    params[:published_at]
  end

  def image_url
    params[:image_url] || image_url_extracted_from_description
  end

  private

  attr_reader :params

  def sanitized_description
    ActionView::Base.full_sanitizer.sanitize(params[:description])
  end

  def image_url_extracted_from_description
    image_html_element && image_html_element.attributes["src"].value
  end

  def image_html_element
    description_as_html.css("img").first
  end

  def description_as_html
    Nokogiri::HTML.fragment(params[:description])
  end
end
