class PageProxy::LinkProxy
  include Rails.application.routes.url_helpers

  LINK_TAG_NAME = "a".freeze
  HTTP_SCHEME = "http".freeze
  SCRIPT_TAG_NAME = "script".freeze
  SCRIPT_MIME_TYPE = "application/x-javascript".freeze

  def initialize(link, tag_name, tag_type)
    @link = PageProxy::UriParser.new(link).parse
    @tag_name = tag_name
    @tag_type = @tag_name == SCRIPT_TAG_NAME ? SCRIPT_MIME_TYPE : tag_type
  end

  def proxied_link
    if external_content?
      proxy_content_path(redirect_url: @link.to_s, type: @tag_type)
    else
      @link
    end
  end

  private

  def external_content?
    @link.scheme == HTTP_SCHEME && @tag_name != LINK_TAG_NAME
  end
end
