class SourceProposalMailer < ApplicationMailer
  def notification(admin:, source:, submitter_email:)
    @source = source
    @submitter_email = submitter_email
    mail(
      to: admin.email,
      subject: I18n.t("mailer.source_proposal.subject", source_name: @source.name)
    )
  end
end
